import os
import re
import asyncio
import discord
from playwright.async_api import async_playwright

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

CHANNEL_ID = 1549512858537041950
GOAL = 360000

GIVE_LIVELY_URL = "https://secure.givelively.org/donate/brave-maker/just-roommates"

intents = discord.Intents.default()
client = discord.Client(intents=intents)


def progress_bar(current, goal, length=20):
    percent = min(current / goal, 1)
    filled = round(percent * length)
    return "█" * filled + "░" * (length - filled)


async def get_funding_total():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)

        page = await browser.new_page()
        await page.goto(GIVE_LIVELY_URL, wait_until="networkidle")

        text = await page.locator("body").inner_text()

        await browser.close()

        print(text)

        match = re.search(
            r'\$([\d,]+(?:\.\d{2})?)\s+raised',
            text,
            re.IGNORECASE
        )

        if not match:
            return None

        return float(match.group(1).replace(",", ""))


@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    channel = client.get_channel(CHANNEL_ID)

    if not channel:
        print("Could not find Discord channel.")
        await client.close()
        return

    total = await get_funding_total()

    if total is None:
        await channel.send(
            "⚠️ I still couldn't read the Give Lively total."
        )
        await client.close()
        return

    percent = (total / GOAL) * 100
    remaining = max(GOAL - total, 0)

    bar = progress_bar(total, GOAL)

    embed = discord.Embed(
        title="🎬 JUST ROOMMATES FUNDING",
        description=f"`{bar}`\n**{percent:.1f}% funded**"
    )

    embed.add_field(
        name="Raised",
        value=f"**${total:,.2f}**",
        inline=True
    )

    embed.add_field(
        name="Goal",
        value=f"**${GOAL:,.0f}**",
        inline=True
    )

    embed.add_field(
        name="Still Needed",
        value=f"**${remaining:,.2f}**",
        inline=False
    )

    embed.set_footer(
        text="Automatically updated from the Just Roommates Give Lively campaign."
    )

    await channel.send(embed=embed)

    await client.close()


client.run(DISCORD_TOKEN)
