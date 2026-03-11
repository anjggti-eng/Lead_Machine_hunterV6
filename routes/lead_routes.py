from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from database.models import db, Lead
from services.bot_service import hunt_leads_master, silent_lead_enricher
from services.ai_service import generate_sales_script, score_lead
from services.geo_service import search_places_geoapify, get_coords_geoapify, search_places_isoline
from sqlalchemy import func
from datetime import datetime, timedelta

leads = Blueprint("leads", __name__)

@leads.route("/dashboard")
@login_required
def dashboard():
    all_leads = Lead.query.order_by(Lead.created_at.desc()).all()
    # Dados para gráficos Sage & Cream
    city_stats = db.session.query(Lead.cidade, func.count(Lead.id)).group_by(Lead.cidade).all()
    city_labels = [s[0] or "N/A" for s in city_stats]
    city_counts = [s[1] for s in city_stats]
    
    seven_days = datetime.utcnow() - timedelta(days=7)
    daily_stats = db.session.query(func.date(Lead.created_at).label('d'), func.count(Lead.id)).filter(Lead.created_at >= seven_days).group_by('d').all()
    date_labels = [str(s[0]) for s in daily_stats]
    date_counts = [s[1] for s in daily_stats]
    
    return render_template("dashboard.html", leads=all_leads, city_labels=city_labels, city_counts=city_counts, date_labels=date_labels, date_counts=date_counts)

@leads.route("/start-hunt", methods=["POST"])
@login_required
def start_hunt():
    if not current_user.is_authenticated:
        return jsonify({"error": "Não autenticado"}), 401
    
    try:
        print("[DEBUG] Start hunt called")
        data = request.json
        query = data.get("query")
        bounds = data.get("bounds")
        center = data.get("center")
        radius = data.get("radius")
        location = data.get("location")
        hunt_type = data.get("type", "radius")
        
        if not query: 
            return jsonify({"error": "Prompt vazio"}), 400
        
        # Se local foi descrito mas não clicado, anexa no query para o Master Hunter
        full_query = query
        if location and not center:
            full_query = f"{query} em {location}"

        # =====================
        # 0. CNPJ direto (OpenCNPJ)
        # =====================
        import re
        from services.cnpj_service import lookup_cnpj

        digits = re.sub(r"\D", "", query or "")
        all_found = []
        if len(digits) == 14:
            print(f"[STAGE 0] Consulta por CNPJ detectada: {digits}")
            info = lookup_cnpj(digits)
            if info:
                # monta lead único a partir dos dados oficiais
                addr_parts = [info.get(k, "") for k in ["logradouro", "numero", "bairro", "municipio", "uf"]]
                address = " ".join([p for p in addr_parts if p])
                phone = ""
                tele = info.get("telefones")
                if tele and isinstance(tele, list) and tele:
                    phone = tele[0].get("numero", "")
                # usar as mesmas chaves que o fluxo Geoapify espera
                all_found.append({
                    "empresa": info.get("razao_social") or info.get("nome_fantasia"),
                    "telefone": phone or "",
                    "endereco": address,
                    "score": 50,
                    "lat": None,
                    "lon": None,
                    "cnpj": digits
                })
                print("[STAGE 0] Lead gerado a partir de OpenCNPJ.")
            else:
                print("[STAGE 0] CNPJ não encontrado na API, seguindo para Geoapify.")

        # Se ainda não preenchemos leads com CNPJ, continua fluxo normal
        if not all_found:
            print(f"[STAGE 1] Buscando leads via Geoapify (Modo: {hunt_type})")
            if hunt_type == "isoline":
                geo_leads = search_places_isoline(query, center, radius)
            else:
                geo_leads = search_places_geoapify(query, bounds=bounds, center=center, radius=radius, location=location)
            print(f"[DEBUG] Geo leads found: {len(geo_leads)}")

            # Mescla os resultados (Prioriza extração rápida e limpa)
            all_found = []

            # 1. Processa Geoapify (Top 10)
            for g in geo_leads[:10]:
                try:
                    print(f"[STAGE 2] Enriquecendo (Scrapy-Style): {g['name']}")
                    phone = silent_lead_enricher(g["name"], g["address"])
                    
                    score = score_lead(g["name"])
                    all_found.append({
                        "empresa": g["name"],
                        "telefone": phone,
                        "endereco": g["address"],
                        "score": score,
                        "lat": g["lat"], "lon": g["lon"]
                    })
                except Exception as e:
                    print(f"[WARN] Erro ao enriquecer lead: {e}")
                    continue

            # Caso não tenha achado nada no Geoapify, apela para o Master como fallback
            if not all_found:
                print("[STAGE 3] API retornou vazio. Ativando Master Hunter Headless...")
                try:
                    found_master = hunt_leads_master(full_query)
                    print(f"[DEBUG] Master leads found: {len(found_master)}")
                    for l in found_master:
                        try:
                            score = score_lead(l["name"])
                            lat, lon = get_coords_geoapify(l["address"])
                            if lat and lon:
                                all_found.append({
                                    "empresa": l["name"],
                                    "telefone": l["whatsapp"],
                                    "endereco": l["address"],
                                    "score": score,
                                    "lat": lat, "lon": lon 
                                })
                        except Exception as e:
                            print(f"[WARN] Erro ao processar lead master: {e}")
                            continue
                except Exception as e:
                    print(f"[WARN] Master Hunter falhou: {e}")

        cidade_query = query.split(" em ")[-1] if " em " in query else "Desconhecida"
        
        for item in all_found:
            try:
                novo = Lead(
                    empresa=item.get("empresa"),
                    telefone=item.get("telefone"),
                    endereco=item.get("endereco"),
                    cidade=cidade_query,
                    score=item.get("score"),
                    lat=item.get("lat"),
                    lon=item.get("lon"),
                    status="novo",
                    cnpj=item.get("cnpj")
                )
                db.session.add(novo)
            except Exception as e:
                print(f"[WARN] Erro ao salvar lead: {e}")
                continue
            
        db.session.commit()
        print(f"[DEBUG] Total leads saved: {len(all_found)}")
        return jsonify({"status": "Sucesso", "message": f"Operação concluída! {len(all_found)} leads capturados e mapeados."})
    
    except Exception as e:
        print(f"[ERROR] Erro geral na busca: {e}")
        return jsonify({"error": f"Erro no servidor: {str(e)[:100]}"}), 500

@leads.route("/generate-script/<int:lead_id>")
@login_required
def get_script(lead_id):
    lead = Lead.query.get_or_404(lead_id)
    script = generate_sales_script(lead.empresa, lead.cidade, lead.telefone)
    return jsonify({"script": script})


@leads.route("/generate-script-all")
@login_required
def get_script_all():
    """Gera pitch de IA para cada lead e devolve lista.
    Usado por botão de "IA para todos" na interface.
    """
    leads_list = Lead.query.all()
    results = []
    for lead in leads_list:
        try:
            script = generate_sales_script(lead.empresa, lead.cidade, lead.telefone)
        except Exception as e:
            script = f"Erro gerando script: {e}"
        results.append({
            "id": lead.id,
            "empresa": lead.empresa,
            "script": script
        })
    return jsonify(results)


@leads.route("/delete-lead/<int:id>", methods=["DELETE"])
@login_required
def delete(id):
    l = Lead.query.get_or_404(id)
    db.session.delete(l)
    db.session.commit()
    return jsonify({"success": True})


# novo endpoint para remoção em massa
@leads.route("/delete-all", methods=["POST"])
@login_required
def delete_all():
    """Limpa toda a tabela de leads."""
    try:
        deleted = Lead.query.delete()
        db.session.commit()
        return jsonify({"success": True, "deleted": deleted})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)[:100]}), 500

