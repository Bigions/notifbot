import discord
import asyncio
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()

# Configurações
TOKEN = os.getenv('DISCORD_TOKEN')
TWITCH_CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
TWITCH_CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
DISCORD_CHANNEL_ID = 1371881513028812830  # Substitua pelo ID real

# Lista de streamers para monitorar
STREAMERS = ["rdulive", "dakotaz", "shroud"]  # Adicione seus streamers aqui

# Configuração dos Intents (OBRIGATÓRIO a partir do discord.py 2.0+)
intents = discord.Intents.default()
intents.message_content = True  # Para ler mensagens (se precisar)

bot = commands.Bot(command_prefix="!", intents=intents)

# Dicionário para armazenar status
streamer_status = {streamer: False for streamer in STREAMERS}

async def get_twitch_access_token():
    """Obtém token de acesso da Twitch"""
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_CLIENT_SECRET,
        "grant_type": "client_credentials"
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(url, params=params) as resp:
            data = await resp.json()
            return data.get("access_token")

async def check_twitch_stream():
    """Verifica status dos streamers"""
    await bot.wait_until_ready()
    channel = bot.get_channel(DISCORD_CHANNEL_ID)
    
    while not bot.is_closed():
        try:
            access_token = await get_twitch_access_token()
            headers = {
                "Client-ID": TWITCH_CLIENT_ID,
                "Authorization": f"Bearer {access_token}"
            }

            for streamer in STREAMERS:
                stream_url = f"https://api.twitch.tv/helix/streams?user_login={streamer}"
                user_url = f"https://api.twitch.tv/helix/users?login={streamer}"

                async with aiohttp.ClientSession() as session:
                    # Pega dados do usuário
                    async with session.get(user_url, headers=headers) as user_resp:
                        user_data = await user_resp.json()
                        profile_image = user_data["data"][0]["profile_image_url"]

                    # Verifica stream
                    async with session.get(stream_url, headers=headers) as stream_resp:
                        data = await stream_resp.json()
                        is_live = "data" in data and len(data["data"]) > 0

                        if is_live and not streamer_status[streamer]:
                            # Configura a mensagem embed
                            embed = discord.Embed(
                                title=f"🔴 {streamer} its LIVE! 🔴",
                                description=data["data"][0]["title"],
                                color=0x9147FF,
                                url=f"https://twitch.tv/{streamer}"
                            )
                            embed.set_image(
                                url=data["data"][0]["thumbnail_url"]
                                .replace("{width}", "1280")
                                .replace("{height}", "720")
                            )
                            await channel.send(embed=embed)
                            streamer_status[streamer] = True
                        
                        elif not is_live and streamer_status[streamer]:
                            streamer_status[streamer] = False

        except Exception as e:
            print(f"Erro: {e}")

        await asyncio.sleep(60)  # Verifica a cada 60 segundos

@bot.event
async def on_ready():
    print(f"{bot.user.name} its here!")
    bot.loop.create_task(check_twitch_stream())

bot.run(TOKEN)

# Mantém o bot ativo (para serviços como Railway/Replit)
from flask import Flask # type: ignore
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot online!"

def run():
    app.run(host='0.0.0.0', port=8000)

def keep_alive():
    from threading import Thread
    t = Thread(target=run)
    t.start()

keep_alive()