import discord
from discord.ext import commands
import datetime
import os
import random
from PIL import Image, ImageDraw, ImageFont

from keep_alive import keep_alive

keep_alive()

bot = commands.Bot(command_prefix=".")

disabled_channels = set()

@bot.command(name='skullboard')
@commands.has_permissions(manage_messages=True)
async def skullboard(ctx, author_id: int, channel: discord.TextChannel, message_content: str, jump_to_message_id: int):
    # Delete user's message
    await ctx.message.delete()

    # Get author's user object
    author = await bot.fetch_user(author_id)

    # Get the jump-to message link
    jump_to_link = f"[Jump To](https://discord.com/channels/{ctx.guild.id}/{channel.id}/{jump_to_message_id})"

    # Create the embed
    embed = discord.Embed(
        title="Skullboard",
        color=discord.Color.dark_grey(),
        description=f"**Author:** {author.mention}\n**Channel:** {channel.mention}\n**Message:** {message_content}\n{jump_to_link}",
        timestamp=datetime.datetime.utcnow()
    )

    # Set author's profile pic as thumbnail
    embed.set_thumbnail(url=author.avatar_url)

    # Set footer with author's ID
    embed.set_footer(text=f"{author.id} | {datetime.datetime.utcnow().strftime('%Y-%m-%d')} | {datetime.datetime.utcnow().strftime('%H:%M:%S')}")

    # Send the embed
    message = await ctx.send(embed=embed)

    # Add reaction to the bot's own message
    await message.add_reaction("💀")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')


@bot.command(name='disabletext')
@commands.has_permissions(manage_messages=True)
async def disable_text(ctx, channel: discord.TextChannel):
    disabled_channels.add(channel.id)
    await ctx.send(f"Text messages are now disabled in {channel.mention}. Users can only send images with text.")

@bot.command(name='enabletext')
@commands.has_permissions(manage_messages=True)
async def enable_text(ctx, channel: discord.TextChannel):
    disabled_channels.discard(channel.id)
    await ctx.send(f"Text messages are now enabled in {channel.mention}. Users can send both text and images.")

@bot.event
async def on_message(message):
    if message.author.bot:
        return  # Ignore messages from bots

    if message.channel.id in disabled_channels and not message.attachments:
        # Delete messages without images in disabled channels
        await message.delete()

        # Send an embed explaining the restriction
        embed = discord.Embed(
            title="Text Messages Disabled",
            description=f"{message.author.mention}, you can't send texts without an image in this channel.",
            color=discord.Color.dark_grey()
        )
        await message.channel.send(embed=embed)

    await bot.process_commands(message)
 
roasts = [
    "You're so ugly, when you were born, the doctor looked at your face and then slapped your mother.",
    "If laughter is the best medicine, your face must be curing the world.",
    "I'd agree with you, but then we'd both be wrong.",
    "Is your ass jealous of the amount of shit that comes out of your mouth?",
    "I'm not saying I hate you, but I would unplug your life support to charge my phone.",
    "You are what happens when women drink during pregnancy.",
    "There is someone out there for everyone. For you, it’s a therapist.",
    "You have such a beautiful face… But let’s put a bag over that personality.",
    "You are the sun in my life… now get 93 million miles away from me.",
    "If I wanted to kill myself, I would simply jump from your ego to your IQ.",
    "If I wanted to kill myself, I would simply jump from your ego to your IQ.",
    "I didn’t mean to offend you… but it was a huge plus.",
    "Whoever told you to be yourself, gave you a bad advice.",
    "I can’t wait to spend my whole life without you.",
    "I don’t know what makes you so stupid, but it works.",
    "Sorry I can’t think of an insult dumb enough for you to understand.",
    "If I throw a stick, will you leave me too?"
]

used_roasts = {}  # To keep track of roasts used for each user

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="SezarX's Meets"))
@bot.command(name='roast')
async def roast_command(ctx, user: discord.Member):
    if user is None:
        await ctx.send("Please specify a user to roast.")
        return

    # Check if roasting is enabled for the user
    if user.id not in used_roasts:
        used_roasts[user.id] = set()

    if user.id in used_roasts and 'roast_off' in used_roasts[user.id]:
        await ctx.send("Roasting is currently turned off for this user.")
        return

    while True:
        # Select a roast that hasn't been used for the specified user
        available_roasts = set(roasts) - used_roasts[user.id]
        if not available_roasts:
            await ctx.send("No more roasts available for this user.")
            return

        roast = random.choice(list(available_roasts))
        used_roasts[user.id].add(roast)

        # Send the roast
        roast_message = await ctx.send(f"{user.mention}, {roast}")

        # Listen for replies and continue roasting
        def reply_check(message):
            return message.author == user and message.reference and message.reference.message_id == roast_message.id

        try:
            reply_message = await bot.wait_for('message', check=reply_check, timeout=60)
        except TimeoutError:
            break  # Stop roasting if no reply within 60 seconds

# Rest of the code remains unchanged
# Prompt user for bot token
bot_token = input("Please enter your bot token: ")
sniped_messages = {}

@bot.event
async def on_message_delete(message):
    sniped_messages[message.channel.id] = {
        "content": message.content,
        "author": str(message.author),
        "timestamp": str(message.created_at),
    }

@bot.command(name='snipe')
@commands.has_permissions(manage_messages=True)
async def snipe_command(ctx):
    channel_id = ctx.channel.id
    if channel_id not in sniped_messages:
        await ctx.send("No recently deleted messages to snipe.")
        return

    sniped_message = sniped_messages[channel_id]
    embed = discord.Embed(
        title="Sniped Message",
        color=discord.Color.blue(),
        description=sniped_message['content']
    )
    embed.set_author(name=sniped_message['author'])
    embed.set_footer(text=f"Deleted at {sniped_message['timestamp']}")

    await ctx.send(embed=embed)

@bot.command(name='text')
@commands.has_permissions(manage_messages=True)
async def text_command(ctx, *, text_to_draw):
    # Send an initial embed with a question about changing the background
    initial_embed = discord.Embed(
        title="Change Background?",
        description="Do you want to change the background?",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=initial_embed)

    # Add reactions (✅ for yes, ❌ for no)
    reactions = ['✅', '❌']
    for reaction in reactions:
        await message.add_reaction(reaction)

    def check(reaction, user):
        return user == ctx.author and str(reaction.emoji) in reactions

    try:
        reaction, _ = await bot.wait_for('reaction_add', timeout=30.0, check=check)
    except TimeoutError:
        await ctx.send("You took too long to respond. The background will not be changed.")
        return

    if str(reaction.emoji) == '✅':
        # Send an embed with background color options
        color_embed = discord.Embed(
            title="Backgrounds",
            description="Please choose a background color by typing it in the chat or select from the list:",
            color=discord.Color.blue()
        )
        color_options = ['black', 'red', 'orange', 'purple', 'green', 'white', 'cyan', 'lime', 'blue', 'lightblue']
        color_embed.add_field(name="Color Options", value=', '.join(color_options))
        await message.edit(embed=color_embed)

        def color_check(msg):
            return msg.author == ctx.author and msg.content.lower() in color_options

        try:
            response = await bot.wait_for('message', timeout=30.0, check=color_check)
        except TimeoutError:
            await ctx.send("You took too long to choose a background color. The default background will be used.")
            return

        # Extract color from the user's message
        color_choice = response.content.lower()

        # Generate image with the chosen background color and text
        image = generate_image(text_to_draw, color_choice)
    else:
        # Generate image with the default background color and text
        image = generate_image(text_to_draw, 'default')

    # Save the image to a file
    image_path = "drawn_image.png"
    image.save(image_path)

    # Send the image to the Discord channel
    await ctx.send(file=discord.File(image_path))

def generate_image(text, background_color):
    # Create a blank image with a white background
    image_size = (300, 150)
    if background_color.lower() == 'default':
        background_color = 'white'
    image = Image.new("RGB", image_size, background_color)

    # Initialize the drawing context
    draw = ImageDraw.Draw(image)

    # Use a basic font (you can replace this with a path to a specific font file)
    font = ImageFont.load_default()

    # Calculate text position
    text_width, text_height = draw.textsize(text, font)
    position = ((image_size[0] - text_width) // 2, (image_size[1] - text_height) // 2)

    # Draw the text on the image
    draw.text(position, text, font=font, fill="black")

    return image

@bot.command(name='lock')
@commands.has_permissions(manage_channels=True)
async def lock_channel(ctx):
    # Check if the channel is already locked
    if ctx.channel.overwrites_for(ctx.guild.default_role).send_messages is False:
        await ctx.send("This channel is already locked.")
        return

    # Deny send_messages permission for @everyone
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
    await ctx.send("Channel locked. Members cannot send messages.")

@bot.command(name='unlock')
@commands.has_permissions(manage_channels=True)
async def unlock_channel(ctx):
    # Check if the channel is already unlocked
    if ctx.channel.overwrites_for(ctx.guild.default_role).send_messages is True:
        await ctx.send("This channel is already unlocked.")
        return

    # Allow send_messages permission for @everyone
    await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=True)
    await ctx.send("Channel unlocked. Members can send messages again.")

@bot.command(name='info')
async def info_command(ctx):
    # Create an embed for the help command
    info_embed = discord.Embed(
        title="BluBot's Commands",
        color=discord.Color.blue()
    )
    info_embed.set_thumbnail(url=bot.user.avatar_url)

    # Add commands to the embed
    commands_info = [
        (".skullboard", "This command is only for staffs", "usage: skullboard <user id/or mention> <channel> <text> <message id>"),
        (".disabletext", "This command is only for staffs", "usage: disabletext <channel mention>\nWhat does it do? This command won't let people send any texts without attaching any images to it."),
        (".enabletext", "This command is only for staffs", "usage: enabletext <channel mention>"),
        (".roast", "Members can use this command", "usage: roast <user mention>\nWhat does it do? It can roast anyone with its Google roast lines."),
        (".snipe", "This command is only for staffs", "usage: .snipe\nWhat does it do? This command will give you the ability to see deleted messages."),
        (".text", "This command is only for staffs", 'usage: .text <whatever you like here>\nWhat does it do? It can put any text into the image.'),
        (".lock", "This command is only for staffs", "usage: go to the channel that you wanna lock and just type .lock\nWhat does it do? Locks the channel."),
        (".unlock", "This command is only for staffs", "usage: go to the channel that you wanna unlock and type .unlock"),
    ]

    for command_name, command_permission, command_description in commands_info:
        info_embed.add_field(
            name=command_name,
            value=f"{command_permission}\n{command_description}",
            inline=False
        )

    
    # Send the help embed
    await ctx.send(embed=info_embed)
  
bot.run(bot_token)

