import discord
from discord.ext import commands
import flask
from flask import Flask, render_template 
from threading import Thread
import os
import json
import psutil
import datetime

app = Flask(__name__)
@app.route('/')
def index():
 return '''<body style="margin: 0; padding: 0;">
<iframe width="100%" height="100%" src="https://axocoder.vercel.app/"frameborder="0"111allowfullscreen></iframe>
</body>'''

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()


keep_alive()
print("Server Running Because of Axo")

# Define your intents
intents = discord.Intents.default()
intents.messages = True  # Enable message-related events
intents.message_content = True  # Enable message content intent
intents.guilds = True  # Enable guild-related events (optional, add more if needed)
# Initialize the bot with a prefix
bot = commands.Bot(command_prefix=".", intents=intents)

      
channel_id = 1187057942030196787  # Replace with your actual channel ID






      # Create a database object to store warnings
warnings_db = {}

      # Load warnings from a file when the bot starts
def load_warnings():
          try:
              with open('warnings.json', 'r') as file:
                  global warnings_db
                  warnings_db = json.load(file)
          except FileNotFoundError:
              warnings_db = {}

      # Save warnings to a file
def save_warnings():
          with open('warnings.json', 'w') as file:
              json.dump(warnings_db, file, indent=2)

      # Check if the user has the "manage messages" permission
def is_mod(ctx):
          return ctx.author.guild_permissions.manage_messages

@bot.event
async def on_ready():
          print(f'Logged in as {bot.user.name}')
          load_warnings()  # Load warnings when the bot starts

@bot.command(name='warn')
@commands.check(is_mod)
async def warn(ctx, member: discord.Member, reason=None):
          # Command to warn a user
          if member:
              if member.id not in warnings_db:
                  warnings_db[member.id] = {'count': 0, 'warnings': []}

              warn_count = warnings_db[member.id]['count'] + 1
              warnings_db[member.id]['count'] = warn_count
              warnings_db[member.id]['warnings'].append({'warner': ctx.author.name, 'reason': reason if reason else 'default'})

              save_warnings()

              embed = discord.Embed(title='User Warned', color=discord.Color.blue())
              embed.add_field(name='User', value=member.mention)
              embed.add_field(name='Warn Count', value=warn_count)
              embed.add_field(name='Reason', value=reason if reason else 'Default')
              await ctx.send(embed=embed)

              # Send a message to the specified channel when a user is warned
              channel = bot.get_channel(channel_id)
              if channel:
                  embed_warning = discord.Embed(title='User Warned', color=discord.Color.orange())
                  embed_warning.add_field(name='User', value=member.mention)
                  embed_warning.add_field(name='Warn Count', value=warn_count)
                  embed_warning.add_field(name='Warner', value=ctx.author.name)
                  embed_warning.add_field(name='Reason', value=reason if reason else 'Default')
                  await channel.send(embed=embed_warning)

@bot.command(name='warnings')
@commands.check(is_mod)
async def get_warnings(ctx, member: discord.Member):
          # Command to check the warnings for a user
          if member.id in warnings_db:
              embed = discord.Embed(title='User Warnings', color=discord.Color.blue())
              embed.add_field(name='User', value=member.mention)

              if warnings_db[member.id]['warnings']:
                  for i, warn in enumerate(warnings_db[member.id]['warnings'], start=1):
                      embed.add_field(
                          name=f'Warning {i}',
                          value=f'**Warner:** {warn["warner"]}\n**Reason:** {warn["reason"]}',
                          inline=False
                      )
              else:
                  embed.add_field(name='No Warnings', value='This user has no warnings.')

              await ctx.send(embed=embed)
          else:
              await ctx.send("This user has no warnings.")

@bot.command(name='clearwarns')
@commands.check(is_mod)
async def clear_warnings(ctx, member: discord.Member):
          # Command to clear warnings for a user
          if member.id in warnings_db:
              embed = discord.Embed(title='Select Warning to Remove', color=discord.Color.blue())
              embed.add_field(name='User', value=member.mention)

              if warnings_db[member.id]['warnings']:
                  for i, warn in enumerate(warnings_db[member.id]['warnings'], start=1):
                      embed.add_field(
                          name=f'Warning {i}',
                          value=f'**Warner:** {warn["warner"]}\n**Reason:** {warn["reason"]}',
                          inline=False
                      )

                  await ctx.send(embed=embed)
                  await ctx.send("Please enter the number of the warning you want to remove:")

                  def check(message):
                      return message.author == ctx.author and message.channel == ctx.channel and message.content.isdigit()

                  try:
                      msg = await bot.wait_for('message', check=check, timeout=30.0)
                      warn_index = int(msg.content) - 1

                      if 0 <= warn_index < len(warnings_db[member.id]['warnings']):
                          removed_warning = warnings_db[member.id]['warnings'].pop(warn_index)
                          warnings_db[member.id]['count'] -= 1
                          save_warnings()
                          await ctx.send(f"Warning {warn_index + 1} removed for {member.mention}. "
                                         f"Warner: {removed_warning['warner']}, Reason: {removed_warning['reason']}")

                          # Update warning positions
                          for i, warn in enumerate(warnings_db[member.id]['warnings']):
                              warn['position'] = i + 1
                      else:
                          await ctx.send("Invalid warning number. Please try again.")
                  except TimeoutError:
                      await ctx.send("Timed out. Please run the command again.")
              else:
                  await ctx.send("This user has no warnings to clear.")
          else:
              await ctx.send("This user has no warnings.")

@bot.event
async def on_command_error(ctx, error):
          if isinstance(error, commands.CheckFailure):
              await ctx.send("You can't run this command, dumbo! You need the 'Manage Messages' permission.")


if __name__ == "__main__":
      # Prompt user for bot token
      bot_token = input("Please enter your bot token: ")

locked_channels = {}

# Check if the user has the "manage channels" permission
def is_mod(ctx):
    return ctx.author.guild_permissions.manage_channels

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command(name='lock')
@commands.check(is_mod)
async def lock_channel(ctx):
    # Command to lock the channel
    channel = ctx.channel

    if channel.id not in locked_channels:
        # Lock the channel
        locked_channels[channel.id] = True
        await channel.set_permissions(ctx.guild.default_role, send_messages=False)

        # Send an experience embed
        embed = discord.Embed(title='Channel Locked 🔒', color=discord.Color.blue())
        embed.add_field(name='Lockdown Experience', value='This channel is now in lockdown mode. Stay tuned for updates!')
        await ctx.send(embed=embed)
    else:
        await ctx.send('This channel is already locked.')

@bot.command(name='unlock')
@commands.check(is_mod)
async def unlock_channel(ctx):
    # Command to unlock the channel
    channel = ctx.channel

    if channel.id in locked_channels:
        # Unlock the channel
        del locked_channels[channel.id]
        await channel.set_permissions(ctx.guild.default_role, send_messages=True)

        # Send an experience embed
        embed = discord.Embed(title='Channel Unlocked 🔓', color=discord.Color.blue())
        embed.add_field(name='Unlock Experience', value='This channel is now unlocked. Feel free to chat!')
        await ctx.send(embed=embed)
    else:
        await ctx.send('This channel is not locked.')

developer_id = 866906565767069736
start_time = datetime.datetime.utcnow()
commands_run = 0  # Counter for commands run

@bot.event
async def on_message(message):
    global commands_run  # Access the global counter

    if message.author.id == developer_id and message.content.lower() == '.info':
        # Check if the command is invoked by the bot developer

        # Calculate ping
        ping = round(bot.latency * 1000)

        # Calculate uptime
        uptime = format_uptime(start_time)

        # Increment the commands_run counter
        commands_run += 1

        # Get GPU and storage information
        gpu_usage = psutil.virtual_memory().percent
        storage_usage = psutil.disk_usage('/').percent

        # Create an embed with the gathered information
        embed = discord.Embed(title="Bot Information", color=discord.Color.blurple())
        embed.add_field(name="Ping", value=f"{ping}ms", inline=True)
        embed.add_field(name="Uptime", value=uptime, inline=True)
        embed.add_field(name="Commands Run", value=commands_run, inline=True)
        embed.add_field(name="GPU Usage", value=f"{gpu_usage}%", inline=True)
        embed.add_field(name="Storage Usage", value=f"{storage_usage}%", inline=True)

        await message.channel.send(embed=embed)

    await bot.process_commands(message)

def format_uptime(start_time):
    delta_uptime = datetime.datetime.utcnow() - start_time
    return str(delta_uptime)

@bot.check
def is_bot_developer(ctx):
    return ctx.author.id == developer_id
if __name__ == "__main__":
  # Prompt user for bot token
  bot_token = input("Please enter your bot token: ") 
  # Run the bot with the provided token
bot.run(bot_token)
