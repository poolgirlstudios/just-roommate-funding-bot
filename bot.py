import os
import re
import requests
import discord

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

CHANNEL_ID = 1549512858537041950
GOAL = 360000

STATS_URL = (
    "https://secure.givelively.org/"
    "donations/brave-maker/stats?campaign=just-roommates"
)

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_funding_total():
    response = requests.get(
        STATS_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    html = response.text

    print("STATS RESPONSE:")
    print(html)

    match = re.search(
        r'data-amount="([\d.]+)"',
        html
    )

    if not match:
        return None

    return float(match.group(1))


def progress_bar(current, goal, length=20):
    percent = min(current / goal, 1)

    # Show at least one filled block once money has been raised
    filled = round(percent * length)

    if current > 0 and filled == 0:
        filled = 1

    return "█" * filled + "░" * (length - filled)


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("Could not find Discord channel.")
        await client.close()
        return

    total = get_funding_total()

    if total is None:
        await channel.send(
            "⚠️ I couldn't read the Give Lively funding total."
        )
        await client.close()
        return

    percent = (total / GOAL) * 100
    remaining = max(GOAL - total, 0)

    bar = progress_bar(total, GOAL)

    embed = discord.Embed(
        title="🎬 JUST ROOMMATES FUNDING",
        description=(
            f"`{bar}`\n"
            f"**{percent:.2f}% funded**"
        )
    )

    embed.add_field(
        name="💗 Raised",
        value=f"**${total:,.0f}**",
        inline=True
    )

    embed.add_field(
        name="🎯 Goal",
        value=f"**${GOAL:,.0f}**",
        inline=True
    )

    embed.add_field(
        name="✨ Still Needed",
        value=f"**${remaining:,.0f}**",
        inline=False
    )

    embed.set_footer(
        text=(
            "Automatically updated from the "
            "Just Roommates Give Lively campaign."
        )
    )

    await channel.send(embed=embed)

    await client.close()


client.run(DISCORD_TOKEN)
