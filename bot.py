from constants import *
import discord
from openai import OpenAI


# Discord bot token
DISCORD_TOKEN = discord_token

# Intents are required for certain Discord events
intents = discord.Intents.default()
intents.message_content = True  # Enable the bot to read messages

# Create the bot client
client = discord.Client(intents=intents)

gpt_client = OpenAI(
    # This is the default and can be omitted
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

# Respond to messages
@client.event
async def on_message(message):
    # Ignore messages from the bot itself
    if message.author == client.user:
        return

    # If message starts with '!ask'
    if message.content.startswith('!ask'):
        prompt = message.content[len('!ask '):].strip()  # Get the user's query after !ask
        if prompt:
            response = ask_gpt(prompt)  # Send the prompt to GPT
            await message.channel.send(response)  # Send the GPT response back to Discord

# Run the bot
client.run(DISCORD_TOKEN)
