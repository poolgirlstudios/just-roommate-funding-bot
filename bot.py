import os
import re
import discord
from playwright.async_api import async_playwright

DISCORD_TOKEN = os.environ["DISCORD_TOKEN"]

CHANNEL_ID = 1549512858537041950
GOAL = 360000

GIVE_LIVELY_URL = "https://secure.givelively.org/donations/brave-maker/just-roommates"

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

        await page.goto(
            GIVE_LIVELY_URL,
            wait_until="domcontentloaded",
            timeout=60000
        )

        # Give Give Lively time to load the live display
        await page.wait_for_timeout(8000)

        all_text = ""

        print("FRAMES FOUND:")

        for i, frame in enumerate(page.frames):
            print(f"FRAME {i}: {frame.url}")

            try:
                text = await frame.locator("body").inner_text(timeout=5000)

                if text.strip():
                    print(f"FRAME {i} TEXT:")
                    print(text)

                    all_text += "\n" + text

            except Exception as e:
                print(f"Could not read frame {i}: {e}")

        await browser.close()

        amounts = re.findall(
            r'\$([\d,]+(?:\.\d{2})?)',
            all_text
        )

        print("AMOUNTS FOUND:", amounts)

        if not amounts:
            return None

        # Ignore the $360,000 goal and use the first other dollar amount.
        for amount in amounts:
            value = float(amount.replace(",", ""))

            if value != GOAL:
                return value

        return None


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
            "⚠️ I couldn't read the Give Lively funding total."
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
