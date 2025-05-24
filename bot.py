import discord
from discord import app_commands
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

guild_id = None  # Remplacez par l'ID de votre serveur pour un déploiement plus rapide des commandes


class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def on_ready(self):
        print(f'Bot connecté en tant que {self.user}')
        if guild_id:
            guild = discord.Object(id=guild_id)
            await self.tree.sync(guild=guild)
        else:
            await self.tree.sync()
        print('Commandes slash synchronisées.')


client = MyClient()


@client.tree.command(name="ping", description="Répond Pong!")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")


@client.tree.command(name="hsr", description="Recherche sur l'API Honkai Star Rail")
@app_commands.describe(query="Votre recherche")
async def hsr(interaction: discord.Interaction, query: str):
    url = f'https://api.honkaistarrail.com/search?query={query}'
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        await interaction.response.send_message(f"Résultat: {data}")
    else:
        await interaction.response.send_message("Erreur lors de la récupération des données.")

if __name__ == '__main__':
    client.run(TOKEN)
