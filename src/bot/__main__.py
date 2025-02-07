import asyncio
import os

import discord
from dotenv import load_dotenv

from .error import ScoreboardError
from .scoreboard import Scoreboard
from .update_tracker import UpdateTracker

load_dotenv()

ALIASES = {"Rayquaza", "Mfiti", "Haku", "Falkor", "Klauth"}
CHECK_INTERVAL = 300
NOTIFICATION_CHANNEL_ID = int(os.getenv("NOTIFICATION_CHANNEL_ID", "0"))


class ScoreboardBot(discord.Bot):
    def __init__(self) -> None:
        super().__init__()
        self.scoreboard = Scoreboard()
        self.update_tracker = UpdateTracker(self.scoreboard, ALIASES)
        self.check_task: asyncio.Task | None = None

    async def start_periodic_check(self) -> None:
        if self.check_task is not None:
            self.check_task.cancel()
        self.check_task = self.loop.create_task(self.periodic_check())

    async def periodic_check(self) -> None:
        channel = self.get_channel(NOTIFICATION_CHANNEL_ID)

        if not isinstance(channel, discord.TextChannel):
            print(f"Could not find notification channel {NOTIFICATION_CHANNEL_ID}")
            return

        while True:
            try:
                updates = self.update_tracker.check_updates()

                if updates:
                    embed = discord.Embed(
                        title="Scoreboard Updates",
                        description=f"Generated at {self.scoreboard.generated_time}",
                        url=self.scoreboard.BASE_URL,
                    )

                    sorted_updates = sorted(
                        updates,
                        key=lambda x: int(x.new_score.split("/")[0])
                        / int(x.new_score.split("/")[1]),
                        reverse=True,
                    )

                    for update in sorted_updates:
                        score_text = (
                            f"{update.new_score}"
                            if update.old_score is None
                            else f"{update.old_score} → {update.new_score}"
                        )

                        embed.add_field(
                            name=update.alias,
                            value=f"[{score_text}]({update.url})",
                            inline=False,
                        )

                    await channel.send(embed=embed)
            except ScoreboardError as e:
                print(f"Error in periodic check: {e}")
                self.update_tracker.previous_time = None

            await asyncio.sleep(CHECK_INTERVAL)


bot = ScoreboardBot()


@bot.event
async def on_ready() -> None:
    print(f"{bot.user} is ready and online!")
    await bot.start_periodic_check()


@bot.slash_command(name="scoreboard", description="Get the current COMP520 scoreboard")
async def scoreboard_command(ctx: discord.ApplicationContext) -> None:
    embeds: list[discord.Embed] = []

    for i in range(0, len(bot.scoreboard.aliases), 25):
        if len(embeds) == 0:
            embed = discord.Embed(
                title="COMP520 Scoreboard",
                url=bot.scoreboard.BASE_URL,
                description=f"Generated at {bot.scoreboard.generated_time}",
                color=discord.Color.blurple(),
            )
        else:
            embed = discord.Embed(color=discord.Color.blurple())

        for alias in bot.scoreboard.aliases[i : i + 25]:
            embed.add_field(name=alias.name, value=alias.passed_tests, inline=False)

        embeds.append(embed)

    await ctx.respond(embeds=embeds)


@bot.slash_command(
    name="scoreboard_internal",
    description="Get the current COMP520 scoreboard, restricted to only our aliases",
)
async def scoreboard_internal_command(ctx: discord.ApplicationContext) -> None:
    embed = discord.Embed(
        title="COMP520 Scoreboard",
        description=f"Generated at {bot.scoreboard.generated_time}",
        url=bot.scoreboard.BASE_URL,
        color=discord.Color.blurple(),
    )

    tracked_aliases = [
        alias for alias in bot.scoreboard.aliases if alias.name in ALIASES
    ]

    for alias in tracked_aliases:
        embed.add_field(
            name=alias.name,
            value=f"[{alias.passed_tests}]({alias.get_results_url(bot.scoreboard.BASE_URL)})",
            inline=False,
        )

    await ctx.respond(embed=embed)


def main() -> None:
    bot.run(os.getenv("DISCORD_BOT_TOKEN"))
