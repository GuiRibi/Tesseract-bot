import discord
# from discord import ui
from discord import app_commands
from discord.ext.commands import MemberConverter

import datetime

async def on_raw_reaction_add(bot, payload):
    # Replace with the ID of your specific message
    specific_message_id = 1265344608498352209
    # Replace with the ID of the role you want to grant
    member_role_id = 1166116351862112386
    community_role_id = 1166116394455269447
    # Replace with the emoji you want to check for
    member_emoji = "tesseract"
    community_emoji = "lut"

    if payload.message_id == specific_message_id:
        guild = bot.get_guild(payload.guild_id)
        if guild is None:
            return
        guild = bot.get_guild(payload.guild_id)

        
        if str(payload.emoji.name) == member_emoji:
            role = guild.get_role(member_role_id)
        elif str(payload.emoji.name) == community_emoji:
            role = guild.get_role(community_role_id)

        if role is None:
            return

        member = guild.get_member(payload.user_id)
        if member is None:
            return

        await member.add_roles(role)
        print(f'Granted {role.name} to {member.display_name}')

async def hello(cmd):
    print('Hello command invoked')
    await cmd.response.send_message(f'Hello {cmd.user.display_name}')

async def send(cmd, channel, *message):
    target_channel = discord.utils.get(cmd.guild.channels, name=channel)

    if target_channel and message != None:
        prmp = ""
        for word in message: prmp += word + " "

        result = await target_channel.send(prmp)
        print(f"message ID: {result.id}")

async def kick(cmd, member: MemberConverter, *, reason=None):
    # Check if the command author has permission to kick members
    if not cmd.author.guild_permissions.kick_members:
        await cmd.send("You don't have permission to kick members.")
        return
    
    if reason is not None:
        reason = "Reason: " + reason
    else: reason = ""
    
    await member.kick(reason=reason)
    await cmd.send(f'{member.mention} has been kicked from the server. {reason}')

async def ban(cmd, member: MemberConverter, *, reason=None):
    # Check if the command author has permission to ban members
    if not cmd.author.guild_permissions.ban_members:
        await cmd.send("You don't have permission to ban members.")
        return
    
    if reason is not None:
        reason = "Reason: " + reason
    else: reason = ""
    
    await member.ban(reason=reason)
    await cmd.send(f'{member.mention} has been banned from the server. {reason}')

async def unban(cmd, *, member):
    # Check if the command author has permission to ban members
    if not cmd.author.guild_permissions.ban_members:
        await cmd.send("You don't have permission to unban members.")
        return

    # Attempt to unban a member by their user ID
    try:
        member_id = int(member)
        banned_users = await cmd.guild.bans()
        for entry in banned_users:
            user = entry.user
            if user.id == member_id:
                await cmd.guild.unban(user)
                await cmd.send(f'{user.mention} has been unbanned.')
                return
        await cmd.send('User not found in the ban list.')
    except ValueError:
        await cmd.send('Please provide a valid user ID for the unban command.')

async def create_channel(cmd,
                         channel_name: str,
                         category_name: str,
                         nsfw: bool
                         ):
    # # Check if the command author has permission to create channels
    # if not cmd.author.guild_permissions.manage_channels:
    #     await cmd.send("You don't have permission to create channels.")
    #     return

    # Find the category by name
    category = discord.utils.get(cmd.guild.categories, name=category_name.lower().capitalize())

    await cmd.response.defer(ephemeral=True)
    # Create the new channel in the specified category
    if category:
        await cmd.guild.create_text_channel(channel_name, category=category, nsfw=nsfw)
        await cmd.followup.send(f"New channel '{channel_name}' has been created in the '{category_name}' category.")
    else:
        await cmd.followup.send(f"Category '{category_name}' not found in the server.")

async def announcement(cmd, 
                       everyone: app_commands.Choice[str],
                       announcement: str
                       ):
    # Find the target channel by name
    target_channel = discord.utils.get(cmd.guild.channels, name="announcements")

    await cmd.response.defer(ephemeral=True)

    message = ""
    
    if everyone.value == "yes":
        message += "@everyone, "

    message += announcement

    # for arg in args:
    #     message += arg + " "

    if target_channel:
        # Create a webhook using the bot's name and avatar
        webhook = await target_channel.create_webhook(name=cmd.user.name)
        
        # Send the message using the webhook
        await webhook.send(message, username=cmd.user.display_name, avatar_url=cmd.user.avatar.url)
        
        # Delete the webhook to avoid clutter
        await webhook.delete()

        await cmd.followup.send("Announcement sent!", ephemeral=True)
        
    else:
        await cmd.followup.send(f"Channel '{target_channel}' not found in the server.")

async def timeout(cmd, member: MemberConverter, duration:int, *, unit, reason=None):
    # Check if the command author has permission to timeout members
    if not cmd.author.guild_permissions.kick_members:
        await cmd.send("You don't have permission to timeout members.")
        return
    
    if(unit == "s"):
        duration=duration
    elif(unit == "m"):
        duration *= 60
    elif(unit == "h"):
        duration*=3600
    elif(unit == "d"):
        duration*= 86400
    else:
        await cmd.send(f"'{unit}' is not a valid unit.")
        return
    
    await member.timeout(datetime.timedelta(seconds=duration), reason=reason)
    await cmd.send(f'{member} has been timed out for {duration} seconds. Reason: {reason}')

async def change_nickname(cmd, member: MemberConverter, new_nickname: str):
    try:
        # Change the member's nickname
        await member.edit(nick=new_nickname)
        print(f"{member.mention}'s nickname has been changed to '{new_nickname}'.")
    except discord.Forbidden:
        print("I don't have permission to change this member's nickname.", ephemeral=True)
    except discord.HTTPException as e:
        print(f"Failed to change nickname: {e}", ephemeral=True)