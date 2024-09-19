import os
from flask import Flask
import multiprocessing
from dotenv import load_dotenv

load_dotenv()

## DISCORD ##
import discord
from discord import app_commands
from discord.ext import commands
from discord.ext.commands import MemberConverter

import DiscordCommands.commands as discordcommands

DISCORDBOT_TOKEN = os.getenv('DISCORDBOT_TOKEN')

## GEMINI ##
from Gemini.gemini import GeminiApi

GEMINI_TOKEN = os.getenv('GEMINI_TOKEN')
MODEL = 'gemini-1.5-flash'
gemini = GeminiApi(GEMINI_TOKEN, MODEL)


## PRODIA ##
from Prodia.prodia import ProdiaApi

PRODIA_TOKEN = os.getenv('PRODIA_TOKEN')
prodia = ProdiaApi(PRODIA_TOKEN)


app = Flask(__name__)


@app.route("/")
def hello_world():
    """Example Hello World route."""
    name = os.environ.get("NAME", "World")
    return f"Hello {name}!"

intents = discord.Intents.all()

bot = commands.Bot(command_prefix = '!', intents=intents)

bot_is_active = True

def is_bot_active():
    async def predicate(interaction: discord.Interaction):
        if bot_is_active:
            return True
        else:
            await interaction.response.send_message("The bot is currently in maintenance mode.", ephemeral=True)
            return False
    return discord.app_commands.check(predicate)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.tree.sync()

@bot.event
async def on_raw_reaction_add(payload):
    await discordcommands.on_raw_reaction_add(bot, payload)

@bot.listen()
async def on_message(message):
    if message.author == '161468598076964864': #Yuiry heheh :P
        if message.attachments:
            url = []
            for attach in message.attachments:
                url.append(attach.url)            

# @bot.listen()
# async def on_message(message):
#     print(message.clean_content, message.attachments.0.url)

@bot.command()
async def watchlist(cmd, member: MemberConverter):
    await cmd.send(f"Added {member} to watchlist\nListening for suspicions activities.")


@bot.command()
async def maintenance(cmd, state=True):
    global bot_is_active

    member_id = 1166123881757691955 #tesseract bot id
    member = cmd.guild.get_member(member_id)

    # Check if the user has permission to use this command
    if not cmd.author.guild_permissions.administrator:
        await cmd.send("You don't have permission to use this command.", ephemeral=True)
        return

    if state in ['on', 'On', 'ON', 'true', 'True', 'TRUE', True]:
        bot_is_active = False
        await discordcommands.change_nickname(cmd, member=member, new_nickname="(Maintenance) Tesseract Bot")
        await cmd.send("Bot is now in maintenance mode.", ephemeral=True)

    elif state in ['off', 'Off', 'OFF', 'false', 'False', 'FALSE', False]:
        bot_is_active = True
        await discordcommands.change_nickname(cmd, member=member, new_nickname="Tesseract Bot")
        await cmd.send("Bot is now active.", ephemeral=True)

    else:
        await cmd.send("Invalid state. Use 'on' or 'off'.", ephemeral=True)

@bot.tree.command(name="hello", description="Says hello")
@is_bot_active()
async def hello(cmd):
    await discordcommands.hello(cmd=cmd)

@bot.command()
@is_bot_active()
async def send(cmd, channel, *message):
    await discordcommands.send(cmd=cmd, channel=channel, *message)

@bot.command()
@is_bot_active()
async def kick(cmd, member: MemberConverter, *, reason=None):
    await discordcommands.kick(cmd=cmd, member=member, reason=reason)

@bot.command()
@is_bot_active()
async def ban(cmd, member: MemberConverter, *, reason=None):
    await discordcommands.ban(cmd=cmd, member=member, reason=reason)

@bot.command()
@is_bot_active()
async def unban(cmd, *, member):
    await discordcommands.unban(cmd=cmd, member=member)

@bot.tree.command(name="create_channel", description="creates a text channel")
@is_bot_active()
async def create_channel(cmd,
                         channel_name: str,
                         category_name: str,
                         nsfw: bool
                         ):
    await discordcommands.create_channel(cmd=cmd, channel_name=channel_name, category_name=category_name, nsfw=nsfw)

@bot.tree.command(name="announcement", description="creates an announcement")
@app_commands.choices(everyone=[
    app_commands.Choice(name="Yes", value="yes"),
    app_commands.Choice(name="No", value="no")
])
@is_bot_active()
async def announcement(cmd, 
                       everyone: app_commands.Choice[str],
                       announcement: str
                       ):
    await discordcommands.announcement(cmd=cmd, everyone=everyone, announcement=announcement)

@bot.command()
@is_bot_active()
async def timeout(cmd, member: MemberConverter, duration:int, *, unit, reason=None):
    await discordcommands.timeout(cmd=cmd, member=member, duration=duration, unit=unit, reason=reason)

@bot.tree.command(name="ai", description="ai assistant")
@is_bot_active()
async def ai(cmd,
             prompt: str,
             private: bool
             ):
    
    await gemini.ai(cmd=cmd, prompt=prompt, private=private)

@bot.tree.command(name="generate", description="ai generated images")
@is_bot_active()
async def generate(cmd,
                   prompt: str,
                   private: bool
                   ):
    await prodia.generate(cmd, prompt, private)

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, discord.app_commands.errors.CheckFailure):
        if not bot_is_active:
            print("maintenance")
        else:
            print(error)
    else:
        # Handle other types of errors here
        pass

def run_flask_server():
    app.run(debug=False, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

async def run_discord_bot():
    await bot.run(DISCORDBOT_TOKEN)

if __name__ == "__main__":
    # Start Flask server in a separate process
    server_process = multiprocessing.Process(target=run_flask_server)
    server_process.start()

    # Run Discord bot in the main thread
    bot.run(DISCORDBOT_TOKEN)