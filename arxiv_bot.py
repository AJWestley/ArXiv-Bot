import os
from datetime import time, datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import arxiv_api
from arxiv_categories import categories, cat_map, emoji_map
from time_utils import today, std_str

CHAR_LIMIT = 1950

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
ASTRO_CHANNEL = os.getenv('ASTRO_CHANNEL')
COMSCI_CHANNEL = os.getenv('COMSCI_CHANNEL')

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@tasks.loop(
    time=time(
        hour=10,
        minute=0,
        tzinfo=ZoneInfo("Africa/Johannesburg")
    )
)
async def daily_message():
    '''Sends the daily arxiv update to all relevant channels'''
    channel_topic = {
        ASTRO_CHANNEL: 'Astrophysics',
        COMSCI_CHANNEL: 'Computer Science'
    }
    for guild in bot.guilds:
        log(f"Sending update to server: {guild.name}")
        for channel in guild.text_channels:
            if channel.name in [ASTRO_CHANNEL, COMSCI_CHANNEL]:
                log(f'Found {channel.name} channel: Sending update.')
                channel = bot.get_channel(channel.id)
                if channel:
                    messages = daily_arxiv_update(channel_topic[channel.name])
                    for msg in messages:
                        await channel.send(msg)
                    log('Update sent.')
                else:
                    log('Failed to send update.')
            else:
                log('No relevant channels found.')
                continue

@bot.event
async def on_ready():
    log(f"Logged in as {bot.user}")
    if not daily_message.is_running():
        daily_message.start()


# ----- Aux Functions -----

def daily_arxiv_update(topic):
    td = today()
    messages = [f'# {emoji_map[topic]} Daily [{topic}](https://arxiv.org/{cat_map[topic]}) Update: {std_str(td)}\n\n']
    papers = arxiv_api.get_all_papers(topic)
    for subtopic in arxiv_api.categories[topic]:
        if subtopic not in papers[topic]:
            continue
        emoji = emoji_map[' '.join([topic, subtopic])]
        topic_msg = [f'## {emoji} [{subtopic}](https://arxiv.org/list/{categories[topic][subtopic]}/new)']
        for p in papers[topic][subtopic]:
            title = p['title']
            authors = ', '.join(p['authors'])
            ID = p['id']
            topic_msg.append(f'### {title}')
            topic_msg.append(f'\t✒️ **Authors**: {authors}')
            topic_msg.append(f'\t🔗 **Link**: https://arxiv.org/{ID}\n')
        while len('\n'.join(topic_msg)) > 1950:
            for _ in range(3):
                topic_msg.pop()
        messages.append('\n'.join(topic_msg))
    return messages

def log(message):
    print(f'{datetime.now().strftime("%d/%m/%Y, %H:%M:%S")} - {message}.')

if __name__ == '__main__':
    bot.run(TOKEN)
