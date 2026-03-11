import requests
from flask import current_app

def search_places_geoapify(query, bounds=None, center=None, radius=None, location=None):
    """
    Usa a API Geoapify Places para buscar empresas de forma instantânea.
    """
    api_key = current_app.config.get("GEOAPIFY_API_KEY")
    if not api_key:
        return []

    # Categorias para máxima cobertura em buscas comerciais e industriais.
    # Em alguns casos a própria query contém pistas que permitem
    # afinar o filtro de categoria (ex: imobiliária, supermercado, etc).
    categories = "commercial"
    qlower = query.lower() if query else ""
    if any(k in qlower for k in ["imobili", "corretor", "imóvel"]):
        categories = "real-estate,commercial"  # real estate businesses têm essa tag no Geoapify
    elif any(k in qlower for k in ["supermercado", "mercearia", "higiene"]):
        categories = "retail,commercial"
    # (outros casos podem ser adicionados aqui futuramente)
    
    if bounds:
        # Se temos bounds (Filtro por área do mapa)
        rect = f"{bounds['sw']['lon']},{bounds['sw']['lat']},{bounds['ne']['lon']},{bounds['ne']['lat']}"
        # incluímos o texto da query para filtrar corretamente dentro do retângulo
        url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=rect:{rect}&text={query}&limit=20&apiKey={api_key}"
    elif center and radius:
        # Se temos centro e raio (Modo Funil)
        # Geoapify espera: lon,lat,radiusMeters
        circle = f"{center['lon']},{center['lat']},{radius}"
        url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=circle:{circle}&bias=proximity:{center['lon']},{center['lat']}&text={query}&limit=50&apiKey={api_key}"
    elif location:
        # Busca por cidade: geocode para place_id
        place_id = get_place_id_geoapify(location)
        if place_id:
            url = f"https://api.geoapify.com/v2/places?categories={categories}&filter=place:{place_id}&text={query}&limit=20&apiKey={api_key}"
        else:
            # mesmo quando não há place_id, adiciona query e localização para minimizar ruídos
            url = f"https://api.geoapify.com/v2/places?categories={categories}&text={query} {location}&limit=20&apiKey={api_key}"
    else:
        # Busca normal por texto
        url = f"https://api.geoapify.com/v2/places?categories={categories}&text={query}&limit=20&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        leads = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [])
            
            if len(coords) >= 2:
                leads.append({
                    "name": props.get("name") or props.get("formatted"),
                    "address": props.get("formatted"),
                    "city": props.get("city") or props.get("state"),
                    "lat": coords[1],
                    "lon": coords[0],
                    "whatsapp": "Pendente",
                })
        return leads
    except Exception as e:
        print(f"[GEOAPIFY] Erro na busca: {e}")
        return []

def get_coords_geoapify(address):
    """
    Geocoding: Converte endereço em Latitude/Longitude.
    """
    api_key = current_app.config.get("GEOAPIFY_API_KEY")
    url = f"https://api.geoapify.com/v1/geocode/search?text={address}&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("features"):
            coords = data["features"][0]["geometry"]["coordinates"]
            return coords[1], coords[0] # lat, lon
    except:
        pass
    return None, None

def get_place_id_geoapify(location):
    """
    Geocoding para obter place_id de uma cidade.
    """
    api_key = current_app.config.get("GEOAPIFY_API_KEY")
    url = f"https://api.geoapify.com/v1/geocode/search?text={location}&type=city&apiKey={api_key}"
    
    try:
        response = requests.get(url, timeout=5)
        data = response.json()
        if data.get("features"):
            props = data["features"][0]["properties"]
            return props.get("place_id")
    except:
        pass
    return None

def search_places_isoline(query, center, radius):
    """
    Busca usando isoline (área alcançável por tempo/distância).
    """
    api_key = current_app.config.get("GEOAPIFY_API_KEY")
    if not api_key:
        return []

    # Usar range em metros (distância)
    range_meters = int(radius)
    mode = "drive"

    isoline_url = f"https://api.geoapify.com/v1/isoline?lat={center['lat']}&lon={center['lon']}&type=distance&mode={mode}&range={range_meters}&apiKey={api_key}"
    
    try:
        response = requests.get(isoline_url, timeout=10)
        response.raise_for_status()
        isoline_data = response.json()
        
        # Obter o ID da geometria
        properties = isoline_data.get("properties", {})
        geometry_id = properties.get("id")
        if not geometry_id:
            return []
        
        # Buscar places dentro da geometria
        places_url = f"https://api.geoapify.com/v2/places?categories=commercial&filter=geometry:{geometry_id}&bias=proximity:{center['lon']},{center['lat']}&text={query}&limit=20&apiKey={api_key}"
        
        response2 = requests.get(places_url, timeout=10)
        response2.raise_for_status()
        data = response2.json()
        
        leads = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            geom = feature.get("geometry", {})
            coords = geom.get("coordinates", [])
            
            if len(coords) >= 2:
                leads.append({
                    "name": props.get("name") or props.get("formatted"),
                    "address": props.get("formatted"),
                    "city": props.get("city") or props.get("state"),
                    "lat": coords[1],
                    "lon": coords[0],
                    "whatsapp": "Pendente",
                })
        return leads
    except Exception as e:
        print(f"[ISOLINE] Erro: {e}")
        return []
