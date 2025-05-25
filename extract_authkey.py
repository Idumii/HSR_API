import browser_cookie3
import requests
import os

def get_authkey():
    try:
        # Récupère les cookies du navigateur Brave
        cookies = browser_cookie3.edge()
        url = "https://hsr.hoyolab.com/gacha"
        
        # Effectue une requête GET avec les cookies
        response = requests.get(url, cookies=cookies)
        
        if response.status_code == 200:
            # Rechercher l'authkey dans le contenu de la réponse
            for line in response.text.splitlines():
                if "authkey=" in line:
                    start = line.find("authkey=") + len("authkey=")
                    end = line.find("&", start)
                    return line[start:end]
        else:
            print(f"Erreur : Statut HTTP {response.status_code}")
    except Exception as e:
        print(f"Erreur lors de la récupération de l'authkey : {e}")
    return None

if __name__ == "__main__":
    authkey = get_authkey()
    if authkey:
        print(f"Authkey trouvée : {authkey}")
    else:
        print("Impossible de trouver l'authkey.")
        
    print("Chemin actuel :", os.getcwd())
    print("Liste des fichiers :", os.listdir())
