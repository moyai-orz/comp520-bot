import os

import discord

from scoreboard import SCOREBOARD_URL, get_scoreboard
from dotenv import load_dotenv

load_dotenv()

bot = discord.Bot()

ALIASES = set(["Rayquaza", "Mfiti", "Haku", "Falkor", "Klauth"])


def handle_error(exception: Exception, ctx: discord.ApplicationContext):
    ctx.respond(exception)


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")


@bot.slash_command(name="scoreboard", description="Get the current COMP520 scoreboard")
async def scoreboard_command(ctx: discord.ApplicationContext):
    """Fetch and display the current COMP520 scoreboard."""

    data = get_scoreboard()

    if data[0]:
        handle_error(data[0], ctx)
        await ctx.respond("Error fetching scoreboard.", ephemeral=True)
        return

    if not data[1]:
        await ctx.respond("No scoreboard data available.", ephemeral=True)
        return

    generated_time = data[1][0]
    fields = data[1][1]

    embeds = []

    for i in range(0, len(fields), 25):
        if len(embeds) == 0:
            embed = discord.Embed(
                title="COMP520 Scoreboard",
                url=SCOREBOARD_URL,
                description=f"Generated at {generated_time}",
                color=discord.Color.blurple(),
            )
        else:
            embed = discord.Embed(color=discord.Color.blurple())

        for alias, url, result in fields[i : i + 25]:
            embed.add_field(name=alias, value=f"{result}", inline=False)

        embeds.append(embed)

    await ctx.respond(embeds=embeds)


@bot.slash_command(
    name="scoreboard_internal",
    description="Get the current COMP520 scoreboard, restricted to only our aliases",
)
async def scoreboard_internal_command(ctx: discord.ApplicationContext):
    data = get_scoreboard()

    if data[0]:
        handle_error(data[0], ctx)
        await ctx.respond("Error fetching scoreboard.", ephemeral=True)
        return

    if not data[1]:
        await ctx.respond("No scoreboard data available.", ephemeral=True)
        return

    generated_time = data[1][0]
    fields = data[1][1]

    for i in range(len(fields)):
        embed = discord.Embed(
            title="COMP520 Scoreboard",
            description=f"Generated at {generated_time}",
            url=SCOREBOARD_URL,
            color=discord.Color.blurple(),
        )

        for alias, url, result in fields:
            if alias not in ALIASES:
                continue

            embed.add_field(name=alias, value=f"[{result}]({url})", inline=False)

    await ctx.respond(embed=embed)


bot.run(os.getenv("DISCORD_BOT_TOKEN"))
