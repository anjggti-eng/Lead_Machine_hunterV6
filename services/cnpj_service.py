import requests

API_URL = "https://api.opencnpj.org/"


def lookup_cnpj(cnpj):
    """Consulta o CNPJ na API pública do OpenCNPJ.

    O parâmetro pode conter pontuação; a função limpta antes de
    concatenar na URL. Retorna dict JSON ou None se não encontrado.
    """
    if not cnpj:
        return None
    # remove qualquer caractere não numérico
    digits = ''.join(ch for ch in cnpj if ch.isdigit())
    if len(digits) != 14:
        return None

    try:
        resp = requests.get(API_URL + digits, timeout=5)
        if resp.status_code == 200:
            return resp.json()
    except Exception:
        pass
    return None
