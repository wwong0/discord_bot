from constants import *
import discord
from openai import OpenAI
import asyncio
import os
import yt_dlp




# Discord bot token
DISCORD_TOKEN = discord_token

# Intents
intents = discord.Intents.default()
intents.message_content = True  # Enable the bot to read messages
intents.guilds = True  # Required for server related events
intents.members = True  # Enable member-related events

# Create the bot client
client = discord.Client(intents=intents)

gpt_client = OpenAI(
    api_key=openai_token,
)

# GPT query function
def ask_gpt(prompt):
    try:
        response = gpt_client.chat.completions.create(
            messages = [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model = "gpt-3.5-turbo",
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error: {e}"

# On bot ready
@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

async def play_music(ctx, url):
    # Join the voice channel
    voice_channel = ctx.author.voice.channel
    voice_client = await voice_channel.connect()

    # Use yt-dlp to get the audio source
    ydl_opts = {
        'format': 'bestaudio',
        'extractaudio': True,
        'audioformat': 'mp3',
        'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        url = info['formats'][0]['url']

    voice_client.play(discord.FFmpegPCMAudio(url), after=lambda e: print(f'Player error: {e}') if e else None)

    # Wait for the audio to finish playing
    while voice_client.is_playing():
        await asyncio.sleep(1)

    await voice_client.disconnect()

# Respond to messages
@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # If message starts with '!ask'
    if message.content.startswith('hey chat'):
        prompt = message.content[len('hey chat'):].strip()  # Get the user's query after !ask
        if prompt:
            response = ask_gpt(prompt)  # Send the prompt to GPT
            await message.channel.send(response)  # Send the GPT response back to Discord

    if message.content.startswith('!mute'):
        muted_role = discord.utils.get(message.guild.roles, name = "muted")
        args = message.content.split()
        member = message.author
        duration = int(args[2]) if len(args) > 2 and args[
            2].isdigit() else 60  # Default to 60 seconds
        if member:
            await member.add_roles(muted_role)
            await asyncio.sleep(duration)
            await member.remove_roles(muted_role)

    if message.content.startswith('!play'):
        if message.author.voice:
            url = message.content[len('!play '):].strip()
            if url:
                await play_music(message, url)
            else:
                await message.channel.send("provide a YouTube URL.")
        else:
            await message.channel.send("not in vc")

# Run the bot
client.run(DISCORD_TOKEN)
