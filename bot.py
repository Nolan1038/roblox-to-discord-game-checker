import os
import discord
import requests
from discord import app_commands
from discord.ext import commands
from keep_alive import keep_alive

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

# Slash command: /trackgame
@tree.command(name="trackgame", description="Track a Roblox game by place ID")
@app_commands.describe(placeid="The placeId of the Roblox game")
async def trackgame(interaction: discord.Interaction, placeid: int):
    await interaction.response.defer()

    # Step 1: Get universeId from placeId
    universe_res = requests.get(f"https://apis.roblox.com/universes/v1/places/{placeid}/universe")
    if universe_res.status_code != 200:
        await interaction.followup.send("❌ Failed to find that place ID.")
        return

    universe_id = universe_res.json().get("universeId")

    # Step 2: Get game info
    games_res = requests.get(f"https://games.roblox.com/v1/games?universeIds={universe_id}")
    if games_res.status_code != 200 or not games_res.json()["data"]:
        await interaction.followup.send("❌ Could not retrieve game info.")
        return

    game = games_res.json()["data"][0]
    name = game["name"]
    updated = game["updated"]

    # Step 3: Get thumbnail
    thumb_res = requests.get(
        f"https://thumbnails.roblox.com/v1/games/icons?universeIds={universe_id}&size=512x512&format=Png&isCircular=false"
    )
    thumb_url = thumb_res.json()["data"][0]["imageUrl"] if thumb_res.status_code == 200 else None

    # Step 4: Build response
    embed = discord.Embed(
        title=name,
        description=f"🆔 Universe ID: `{universe_id}`\n🕒 Last Updated: `{updated}`",
        color=discord.Color.green()
    )

    if thumb_url:
        embed.set_thumbnail(url=thumb_url)

    await interaction.followup.send(embed=embed)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Logged in as {bot.user}")

keep_alive()
bot.run(os.getenv("DISCORD_TOKEN"))
