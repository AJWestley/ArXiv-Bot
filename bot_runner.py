import os
from dotenv import load_dotenv
from src.arxivist import ArXivist

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

update_hour = 10
update_min = 0

bot = ArXivist((update_hour, update_min), 'channels.json', 'taxonomy.json', 'filtering.json', timezone="Africa/Johannesburg")

bot.run(TOKEN)