import sys
print(sys.executable)
from dotenv import load_dotenv
import os
import requests
from discord import app_commands
import discord
from discord.ui import Button, View
import genshin
import urllib.parse

# API pour commandes codes et calendrier
# https://github.com/torikushiii/hoyoverse-api



load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

guild_id = os.getenv('GUILD_ID')


intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@client.event
async def on_ready():
    try:
        if guild_id:
            guild = discord.Object(id=guild_id)
            await tree.sync(guild=guild)
            print(f'Commandes slash synchronisées pour le serveur : {guild_id}')
        else:
            await tree.sync()
            print('Commandes slash synchronisées globalement.')
    except Exception as e:
        print(f'Erreur lors de la synchronisation des commandes : {e}')


@tree.command(name="ping", description="Répond Pong!", guild=discord.Object(id=guild_id))
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@tree.command(name="hsr", description="Recherche sur l'API Honkai Star Rail", guild=discord.Object(id=guild_id))
@app_commands.describe(query="UID du joueur")
async def hsr(interaction: discord.Interaction, query: str):
    url = f'https://api.honkaistarrail.com/search?query={query}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        await interaction.response.send_message(f"Résultat: {data}")
    else:
        await interaction.response.send_message("Erreur lors de la récupération des données.")
        
        
        
@tree.command(name="codes", description="Codes actifs selon le jeu choisi", guild=discord.Object(id=guild_id))
@app_commands.describe(game="Choix du jeu")
@app_commands.choices(game=[
    app_commands.Choice(name="Honkai Star Rail", value="starrail"),
    app_commands.Choice(name="Genshin Impact", value="genshin"),
    app_commands.Choice(name="Tears of Themis", value="themis"),
    app_commands.Choice(name="Honkai Impact 3rd", value="honkai"),
    app_commands.Choice(name="Zenless Zone Zero", value="zenless")
])
async def codes(interaction: discord.Interaction, game: str):
    games_dict = {
        "starrail": "Honkai Star Rail",
        "genshin": "Genshin Impact",
        "themis": "Tears of Themis",
        "honkai": "Honkai Impact 3rd",
        "zenless": "Zenless Zone Zero"
    }
    
    
    """Récupère les codes actifs pour le jeu spécifié."""
    url = f'https://api.ennead.cc/mihoyo/{game}/codes'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        active_codes = data.get("active", [])
        if not active_codes:
            await interaction.response.send_message(f"Aucun code actif trouvé pour le jeu {game}.")
            return
        message = f"Codes actifs pour le jeu {games_dict[game]} :\n"
        for code in active_codes:
            rewards_list = code.get('reward', [])
            if rewards_list:
                rewards = ', '.join(rewards_list)
            else:
                rewards = 'Aucune récompense renseignée'
            message += f"• {code['code']} : {rewards}\n"
        await interaction.response.send_message(message)
    else:
        await interaction.response.send_message("Erreur lors de la récupération des données.")        

@tree.command(name="calendar", description="Événements, bannières et challenges selon le jeu choisi", guild=discord.Object(id=guild_id))
@app_commands.describe(game="Choix du jeu")
@app_commands.choices(game=[
    app_commands.Choice(name="Honkai Star Rail", value="starrail"),
    app_commands.Choice(name="Genshin Impact", value="genshin"),
    app_commands.Choice(name="Tears of Themis", value="themis"),
    app_commands.Choice(name="Honkai Impact 3rd", value="honkai"),
    app_commands.Choice(name="Zenless Zone Zero", value="zenless")
])
async def calendar(interaction: discord.Interaction, game: str):
    import datetime

    def format_timestamp(ts):
        # Si le timestamp est en millisecondes (plus de 10 chiffres), on le convertit en secondes
        if ts > 1e10:
            ts = ts / 1000
        return datetime.datetime.fromtimestamp(ts).strftime('%d/%m/%Y')

    games_dict = {
        "starrail": "Honkai Star Rail",
        "genshin": "Genshin Impact",
        "themis": "Tears of Themis",
        "honkai": "Honkai Impact 3rd",
        "zenless": "Zenless Zone Zero"
    }
    
    url = f'https://api.ennead.cc/mihoyo/{game}/calendar'
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        message = f"Calendrier pour le jeu {games_dict[game]} :\n"
        
        # Events
        events = data.get("events", [])
        if events:
            message += "\n__Événements :__\n"
            for event in events:
                name = event.get('name', 'Sans nom')
                start = format_timestamp(event.get('start_time', 0))
                end = format_timestamp(event.get('end_time', 0))
                message += f"• {name}\n  Du {start} au {end}\n"
        
        # Banners
        banners = data.get("banners", [])
        if banners:
            message += "\n__Bannières :__\n"
            for banner in banners:
                name = banner.get('name', 'Sans nom')
                version = banner.get('version', '?')
                start = format_timestamp(banner.get('start_time', 0))
                end = format_timestamp(banner.get('end_time', 0))
                chars = [c.get('name', '?') for c in banner.get('characters', [])]
                chars_str = ', '.join(chars) if chars else 'Aucun'
                message += f"• {name} (Ver. {version})\n  Du {start} au {end}\n  Personnages : {chars_str}\n"
        
        # Challenges
        challenges = data.get("challenges", [])
        if challenges:
            message += "\n__Défis :__\n"
            for challenge in challenges:
                name = challenge.get('name', 'Sans nom')
                start = format_timestamp(challenge.get('start_time', 0))
                end = format_timestamp(challenge.get('end_time', 0))
                message += f"• {name}\n  Du {start} au {end}\n"
        
        await interaction.response.send_message(message)
    else:
        await interaction.response.send_message("Erreur lors de la récupération des données.")
        
        

# Command pour afficher le profil HSR d'un compte enregistré
@tree.command(name="profile", description="Affiche le profil HSR d'un compte enregistré", guild=discord.Object(id=guild_id))
@app_commands.describe(pseudo="Sélectionner un compte")
@app_commands.choices(pseudo=[
    app_commands.Choice(name="Idumi", value="Idumi"),
    app_commands.Choice(name="Masuri", value="Masuri"),
    app_commands.Choice(name="Muun", value="Muun"),
    app_commands.Choice(name="FroFrotte", value="FroFrotte")
])
async def profile(interaction: discord.Interaction, pseudo: str):
    try:
        # Récupération des tokens et UID selon le pseudo
        ltuid = os.getenv(f"LTUID_{pseudo}")
        ltoken = os.getenv(f"LTOKEN_{pseudo}")
        uid = os.getenv(f"UID_{pseudo}")
        
        if not all([ltuid, ltoken, uid]):
            await interaction.response.send_message("Erreur : Informations de compte manquantes.")
            return
            
        # Création du client avec les tokens correspondants
        client = genshin.Client({
            "ltuid_v2": ltuid,
            "ltoken_v2": ltoken
        })        # Récupération des données HSR du compte sélectionné
        data = await client.get_starrail_user(uid)
        
        # Debug - Affichage détaillé des données disponibles
        try:
            print("\n=== Données de base ===")
            print("Attributs disponibles sur data:")
            for attr in dir(data):
                if not attr.startswith('_'):
                    print(f"{attr}: {getattr(data, attr)}")

            print("\n=== Détails des personnages ===")
            detailed_data = await client.get_starrail_characters(uid)
            for char in detailed_data:
                print(f"\nPersonnage: {char.name}")
                for attr in dir(char):
                    if not attr.startswith('_'):
                        print(f"  {attr}: {getattr(char, attr)}")

            print("\n=== Mémoire d'Herta ===")
            sim_universe = await client.get_starrail_forgotten_hall(uid)
            for attr in dir(sim_universe):
                if not attr.startswith('_'):
                    print(f"{attr}: {getattr(sim_universe, attr)}")
        except Exception as e:
            print(f"Erreur lors de la récupération des données détaillées: {e}")
          # Création de l'embed
        embed = discord.Embed(
            title=f"Profil HSR de {data.info.nickname}",
            color=0x2b2d31  # Couleur gris foncé
        )
        
        # Création de la vue avec les boutons
        class ProfileView(discord.ui.View):
            def __init__(self, uid: str, client: genshin.Client):
                super().__init__(timeout=60)  # 60 secondes de timeout
                self.uid = uid
                self.client = client

            @discord.ui.button(label="Détails des personnages", style=discord.ButtonStyle.primary)
            async def show_characters(self, interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    detailed_data = await self.client.get_starrail_characters(self.uid)
                    char_embed = discord.Embed(
                        title=f"Détails des personnages de {data.info.nickname}",
                        color=0x2b2d31
                    )
                    # TODO: Ajouter les détails des personnages
                    await interaction.response.send_message(embed=char_embed, ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"Erreur : {str(e)}", ephemeral=True)

            @discord.ui.button(label="Mémoire d'Herta", style=discord.ButtonStyle.primary)
            async def show_abyss(self, interaction: discord.Interaction, button: discord.ui.Button):
                try:
                    abyss_data = await self.client.get_starrail_forgotten_hall(self.uid)
                    abyss_embed = discord.Embed(
                        title=f"Mémoire d'Herta de {data.info.nickname}",
                        color=0x2b2d31
                    )
                    # TODO: Ajouter les détails de la Mémoire d'Herta
                    await interaction.response.send_message(embed=abyss_embed, ephemeral=True)
                except Exception as e:
                    await interaction.response.send_message(f"Erreur : {str(e)}", ephemeral=True)

        # Avatar du joueur s'il est disponible
        if hasattr(data.info, 'avatar'):
            embed.set_thumbnail(url=data.info.avatar)

        # Informations de base
        embed.add_field(
            name="Informations",
            value=f"Niveau : {data.info.level}\n",
            inline=False
        )

        # Statistiques
        stats_text = (
            f"Jours actifs : {data.stats.active_days}\n"
            f"Achievements : {data.stats.achievement_num}\n"
            f"Coffres ouverts : {data.stats.chest_num}\n"
            f"Personnages : {data.stats.avatar_num}"
        )
        embed.add_field(name="Statistiques", value=stats_text, inline=False)

        # Personnages principaux (niveau 50+, limité à 15)
        if data.characters:
            # Trie tous les personnages par niveau, rareté et nom
            sorted_chars = sorted(
                data.characters,
                key=lambda x: (-x.level, -x.rarity, x.name)
            )
            
            # Prend les 15 premiers personnages
            top_chars = sorted_chars[:15]
            
            if top_chars:
                chars_text = ""
                element_emoji = {
                    "fire": "🔥", "ice": "❄️", "lightning": "⚡",
                    "wind": "🌪️", "quantum": "⚛️", "imaginary": "✨",
                    "physical": "👊"
                }
                
                for char in top_chars:
                    emoji = element_emoji.get(char.element, "")
                    level_text = f"Nv.{char.level}"
                    chars_text += f"{emoji} **{char.name}** - {level_text} ({char.rarity}⭐) [C{char.rank}]\n"
                
                if len(sorted_chars) > 15:
                    chars_text += f"\n*+ {len(sorted_chars) - 15} autres personnages...*"
                
                embed.add_field(name="Personnages principaux", value=chars_text, inline=False)        # Footer avec l'UID
        embed.set_footer(text=f"UID: {uid}")

        # Création de la vue avec les boutons
        view = ProfileView(uid, client)
        
        # Envoi du message avec l'embed et les boutons
        await interaction.response.send_message(embed=embed, view=view)
    except Exception as e:
        await interaction.response.send_message(f"Erreur lors de la récupération des données : {str(e)}")

@tree.command(name="wishes", description="Affiche l'historique des invocations HSR", guild=discord.Object(id=guild_id))
@app_commands.describe(pseudo="Sélectionner un compte", limit="Nombre d'invocations à afficher (max 100)")
@app_commands.choices(pseudo=[
    app_commands.Choice(name="Idumi", value="Idumi"),
    app_commands.Choice(name="Masuri", value="Masuri"),
    app_commands.Choice(name="Muun", value="Muun"),
    app_commands.Choice(name="FroFrotte", value="FroFrotte")
])
async def wishes(interaction: discord.Interaction, pseudo: str, limit: int = 20):
    try:
        # Récupération de l'authkey depuis le fichier .env
        authkey = os.getenv(f"AUTHKEY_{pseudo}")

        if not authkey:
            await interaction.response.send_message("Erreur : Authkey manquante pour ce compte.")
            return

        # Initialisation des paramètres
        authkey_encoded = urllib.parse.quote(authkey, safe='')
        gacha_type = "11"  # Exemple : bannière standard
        page = 1
        size = min(limit, 100)
        end_id = 0
        all_wishes = []

        # Récupération des invocations avec pagination
        while len(all_wishes) < limit:
            url = (
                f"https://public-operation-hkrpg-sg.hoyoverse.com/common/gacha_record/api/getGachaLog"
                f"?authkey={authkey_encoded}&authkey_ver=1&sign_type=2&lang=fr&size={size}&page={page}"
                f"&game_biz=hkrpg_global&gacha_type={gacha_type}&end_id={end_id}"
            )
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                if not data['data']['list']:
                    break  # Arrêter si aucune donnée supplémentaire
                all_wishes.extend(data['data']['list'])
                end_id = data['data']['list'][-1]['id']  # Mettre à jour l'ID de fin
                page += 1
            else:
                await interaction.response.send_message(f"Erreur : {response.status_code}, Réponse : {response.text}")
                return

        # Limiter les résultats au nombre demandé
        all_wishes = all_wishes[:limit]

        # Formatage des résultats
        if all_wishes:
            wishes_text = "\n".join(
                f"{wish['time']} - {wish['name']} ({wish['rank_type']}★) - {wish['item_type']}"
                for wish in all_wishes
            )
            await interaction.response.send_message(f"Invocations récupérées :\n{wishes_text}")
        else:
            await interaction.response.send_message("Aucune invocation trouvée.")

    except Exception as e:
        await interaction.response.send_message(f"Erreur : {str(e)}")

client.run(TOKEN)
