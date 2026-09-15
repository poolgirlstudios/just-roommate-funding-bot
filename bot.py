import os
import requests
import discord

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

CHANNEL_ID = 1549512858537041950
GOAL = 360000

DATA_URL = (
    "https://secure.givelively.org/donations/brave-maker/"
    "just-roommates.json?last_donation_date=2026-09-15T17:26:23.000Z"
)

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def get_funding_data():
    response = requests.get(
        DATA_URL,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    response.raise_for_status()

    data = response.json()

    total = float(data["newTotalAmount"])
    donor_count = int(data["newDonorCount"])

    return total, donor_count


def progress_bar(current, goal, length=20):
    percent = min(current / goal, 1)
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

    try:
        total, donor_count = get_funding_data()
    except Exception as e:
        print(f"Give Lively error: {e}")

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
        value=f"**${total:,.2f}**",
        inline=True
    )

    embed.add_field(
        name="🎯 Goal",
        value=f"**${GOAL:,.0f}**",
        inline=True
    )

    embed.add_field(
        name="👥 Donors",
        value=f"**{donor_count:,}**",
        inline=True
    )

    embed.add_field(
        name="✨ Still Needed",
        value=f"**${remaining:,.2f}**",
        inline=False
    )

    embed.set_footer(
        text="Automatically updated from the Just Roommates Give Lively campaign."
    )

    await channel.send(embed=embed)

    await client.close()


client.run(DISCORD_TOKEN)
