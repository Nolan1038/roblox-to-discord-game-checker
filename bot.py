import discord
from discord.ext import commands
from discord import app_commands
import requests
from datetime import datetime
from keep_alive import keep_alive

keep_alive()  # Keeps the bot alive on Render


TOKEN = "GtjfmxZMf1ZdNw2ZsINJmTHP-_yIqpOL"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

class GameTracker(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="trackgame", description="Track a Roblox game's last update and thumbnail")
    @app_commands.describe(game_id="Roblox universe ID (not place ID)")
    async def trackgame(self, interaction: discord.Interaction, game_id: str):
        try:
            # Get game info
            game_url = f"https://games.roblox.com/v1/games?universeIds={game_id}"
            game_res = requests.get(game_url).json()
            if not game_res["data"]:
                await interaction.response.send_message("❌ Invalid universe ID or game not found.", ephemeral=True)
                return

            game_data = game_res["data"][0]
            title = game_data["name"]
            updated = datetime.strptime(game_data["updated"], "%Y-%m-%dT%H:%M:%S.%fZ")
            updated_str = updated.strftime("%B %d, %Y %H:%M UTC")

            # Get thumbnail
            thumb_url = f"https://thumbnails.roblox.com/v1/games/icons?universeIds={game_id}&format=Png&size=512x512"
            thumb_res = requests.get(thumb_url).json()
            thumb_link = thumb_res["data"][0]["imageUrl"]

            # Create embed
            embed = discord.Embed(title=title, description=f"Roblox Universe ID: `{game_id}`", color=0x00B2FF)
            embed.add_field(name="🕒 Last Updated", value=updated_str, inline=False)
            embed.set_thumbnail(url=thumb_link)
            embed.set_footer(text="Roblox Game Tracker")

            await interaction.response.send_message(embed=embed)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error: {str(e)}", ephemeral=True)

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"🤖 Logged in as {bot.user} and slash commands synced.")

async def setup_bot():
    await bot.add_cog(GameTracker(bot))

bot.loop.create_task(setup_bot())
bot.run(TOKEN)
