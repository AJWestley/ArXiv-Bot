import os
from dotenv import load_dotenv
from src.arxivist import ArXivist

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
CHANNEL = os.getenv('CHANNEL_FILE')
TAXONOMY = os.getenv('TAXONOMY_FILE')
FILTER = os.getenv('FILTERING_FILE')

bot = ArXivist((23, 50), CHANNEL, TAXONOMY, FILTER, timezone="Africa/Johannesburg")

bot.run(TOKEN)