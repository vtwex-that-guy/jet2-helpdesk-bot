import discord
from discord.ext import commands
import sqlite3
import json

with open("config.json") as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)
conn = sqlite3.connect("database.db")
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS tickets (
    user_id INTEGER PRIMARY KEY,
    status TEXT,
    thread_id INTEGER
)""")
conn.commit()

@bot.event
async def on_ready():
    print(f"Jet2 Helpdesk Bot is online as {bot.user}.")

@bot.slash_command(guild_ids=[int(config["guild_id"])], description="Open a helpdesk ticket")
async def modmail(ctx: discord.ApplicationContext, message: str):
    user_id = ctx.author.id
    c.execute("SELECT * FROM tickets WHERE user_id=?", (user_id,))
    data = c.fetchone()

    if data and data[1] == "open":
        await ctx.respond("❗ You already have an open ticket.", ephemeral=True)
        return

    channel = bot.get_channel(int(config["modmail_channel_id"]))
    embed = discord.Embed(title="📨 New Modmail Ticket", color=discord.Color.red())
    embed.add_field(name="From", value=f"{ctx.author} ({ctx.author.id})", inline=False)
    embed.add_field(name="Message", value=message, inline=False)

    thread = await channel.create_thread(name=f"Ticket - {ctx.author}", type=discord.ChannelType.private_thread)
    await thread.send(embed=embed)

    c.execute("INSERT OR REPLACE INTO tickets (user_id, status, thread_id) VALUES (?, ?, ?)", (user_id, "open", thread.id))
    conn.commit()

    await ctx.respond("✅ Your message has been sent to the Jet2 helpdesk. A staff member will respond soon.", ephemeral=True)

@bot.slash_command(guild_ids=[int(config["guild_id"])], description="Reply to a user ticket")
@commands.has_any_role(*config["admin_roles"])
async def reply(ctx: discord.ApplicationContext, user: discord.User, message: str):
    c.execute("SELECT * FROM tickets WHERE user_id=?", (user.id,))
    data = c.fetchone()
    if not data or data[1] != "open":
        await ctx.respond("❌ No open ticket found for this user.", ephemeral=True)
        return

    await user.send(f"✈️ **Jet2 Helpdesk Reply**:
{message}")
    await ctx.respond(f"✅ Message sent to {user.name}", ephemeral=True)

@bot.slash_command(guild_ids=[int(config["guild_id"])], description="Close a modmail ticket")
@commands.has_any_role(*config["admin_roles"])
async def close(ctx: discord.ApplicationContext, user: discord.User):
    c.execute("SELECT * FROM tickets WHERE user_id=?", (user.id,))
    data = c.fetchone()

    if not data:
        await ctx.respond("❌ No ticket found.", ephemeral=True)
        return

    c.execute("DELETE FROM tickets WHERE user_id=?", (user.id,))
    conn.commit()
    await ctx.respond(f"🛑 Ticket with {user.mention} has been closed.", ephemeral=True)

    try:
        await user.send("📪 Your Jet2 Helpdesk ticket has been closed. Thank you for contacting us.")
    except:
        pass

bot.run(config["token"])
