import json
from datetime import time, datetime
from zoneinfo import ZoneInfo
import discord
from discord.ext import commands, tasks

from src.ArXiv_API.web_api import get_papers
from src.ArXiv_API.arxiv_categories import load_taxonomy_from_json
from src.utils.relevance_filter import load_relevance_filter_from_json
from src.utils.time_utils import today, yesterday, std_str

CHAR_LIMIT = 1950

class ArXivist:
    def __init__(
            self, 
            time: tuple[int, int],
            channel_json_path: str,
            taxonomy_json_path: str, 
            filter_json_path: str,
            timezone: str = 'UTC'
        ):
        self.__hour, self.__minute = time
        self.__timezone = timezone

        intents = discord.Intents.default()
        intents.message_content = True
        self.__bot = commands.Bot(command_prefix="!", intents=intents)

        self.__taxonomy = load_taxonomy_from_json(taxonomy_json_path)
        self.__filter = load_relevance_filter_from_json(filter_json_path)
        self.__channels = load_channels_from_json(channel_json_path)

        self.__setup_loop()
        self.__setup_events()

    def __setup_loop(self):
        scheduled_time = time(
            hour=self.__hour,
            minute=self.__minute,
            tzinfo=ZoneInfo(self.__timezone)
        )

        @tasks.loop(time=scheduled_time)
        async def daily_message():
            for guild in self.__bot.guilds:
                log(f"Sending update to server: {guild.name}")
                for channel in guild.text_channels:
                    if channel.name in self.__channels:
                        log(f'Found {channel.name} channel: Sending update.')
                        fetched = self.__bot.get_channel(channel.id)
                        if fetched:
                            for topic in self.__channels[channel.name]:
                                messages = self.__daily_arxiv_update(topic)
                                for msg in messages:
                                    await fetched.send(msg)
                            log('Update sent.')
                        else:
                            log('Failed to send update.')

        self.__daily_message = daily_message

    def __setup_events(self):
        @self.__bot.event
        async def on_ready():
            log(f"Logged in as {self.__bot.user}")
            if not self.__daily_message.is_running():
                self.__daily_message.start()
    
    def __get_all_papers(self, field: str):
        if not isinstance(field, str):
            raise TypeError(f'fields must be a list or str, but is of type {type(fields)}.')
        day = yesterday()
        cats = self.__taxonomy.get_valid_categories(field)
        papers = get_papers(day, cats)
        papers = self.__filter.filter_relevant(papers)

        papers = self.__taxonomy.group_by_category(papers)
        return papers
    
    def __daily_arxiv_update(self, topic: str):
        td = std_str(today())
        topic_emoji = self.__taxonomy.get_emoji(topic)
        topic_code = self.__taxonomy.get_code(topic)
        messages = [f'# {topic_emoji} Daily [{topic}](https://arxiv.org/{topic_code}) Update: {td}\n\n']

        papers = self.__get_all_papers(topic)

        subtopics = self.__taxonomy[topic]['subfields']

        for subtopic in subtopics:
            if subtopic not in papers[topic]:
                continue

            subtopic_emoji = self.__taxonomy.get_emoji(topic, subtopic)
            subtopic_code = self.__taxonomy.get_code(topic, subtopic)

            topic_msg = [f'## {subtopic_emoji} [{subtopic}](https://arxiv.org/list/{subtopic_code}/new)']

            for p in papers[topic][subtopic]:
                title = p['title']
                authors = ', '.join(p['authors'])
                ID = p['id']
                topic_msg.append(f'### {title}')
                topic_msg.append(f'\t✒️ **Authors**: {authors}')
                topic_msg.append(f'\t🔗 **Link**: {ID}\n')
            while len('\n'.join(topic_msg)) > CHAR_LIMIT:
                for _ in range(3):
                    topic_msg.pop()
            messages.append('\n'.join(topic_msg))
        return messages

    def run(self, token: str):
        ''' Runs the ArXivist with the given Discord API token '''
        self.__bot.run(token)


# ----- Aux Functions -----

def log(message):
    print(f'{datetime.now().strftime("%d/%m/%Y, %H:%M:%S")} - {message}.')

def load_channels_from_json(filepath: str):
    '''
    Loads channel data from a json config file.
    '''
    with open(filepath) as file:
        config = json.load(file)
    return config
