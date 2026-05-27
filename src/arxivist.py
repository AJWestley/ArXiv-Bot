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
    """
    A Discord bot that fetches and posts daily ArXiv paper updates to configured channels.

    The bot runs on a scheduled loop, retrieving papers published the previous day,
    filtering them for relevance, grouping them by category, and posting formatted
    summaries to the appropriate Discord channels.

    Attributes:
        __hour (int): The hour at which the daily update is scheduled.
        __minute (int): The minute at which the daily update is scheduled.
        __timezone (str): The timezone string used for scheduling (e.g. 'UTC', 'US/Eastern').
        __bot (commands.Bot): The underlying Discord bot instance.
        __taxonomy: The ArXiv category taxonomy loaded from JSON.
        __filter: The relevance filter loaded from JSON.
        __channels (dict): A mapping of channel names to their subscribed topics.
    """
    def __init__(
            self, 
            time: tuple[int, int],
            channel_json_path: str,
            taxonomy_json_path: str, 
            filter_json_path: str,
            timezone: str = 'UTC'
        ):
        """
        Initialises the ArXivist bot with scheduling, channel, taxonomy, and filter config.

        Args:
            time (tuple[int, int]): A (hour, minute) tuple specifying when to post daily updates.
            channel_json_path (str): Path to the JSON file mapping channel names to topics.
            taxonomy_json_path (str): Path to the JSON file defining the ArXiv category taxonomy.
            filter_json_path (str): Path to the JSON file defining the relevance filter.
            timezone (str): Timezone string for scheduling the daily loop. Defaults to 'UTC'.
        """
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
        """
        Configures the daily scheduled task that sends ArXiv updates to Discord channels.

        Iterates over all guilds and their text channels, posting topic-specific updates
        to any channel whose name appears in the configured channels mapping.
        """
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
        """
        Registers Discord event handlers on the bot.

        Currently registers an on_ready handler that logs the bot's identity
        and starts the daily message loop if it is not already running.
        """
        @self.__bot.event
        async def on_ready():
            log(f"Logged in as {self.__bot.user}")
            if not self.__daily_message.is_running():
                self.__daily_message.start()
    
    def __get_all_papers(self, field: str):
        """
        Fetches, filters, and groups yesterday's papers for a given top-level field.

        Args:
            field (str): The top-level ArXiv field to retrieve papers for (e.g. 'Physics').

        Returns:
            dict: Papers grouped by category, as returned by the taxonomy's group_by_category method.

        Raises:
            TypeError: If field is not a string.
        """
        if not isinstance(field, str):
            raise TypeError(f'fields must be a list or str, but is of type {type(fields)}.')
        day = yesterday()
        cats = self.__taxonomy.get_valid_categories(field)
        papers = get_papers(day, cats)
        papers = self.__filter.filter_relevant(papers)

        papers = self.__taxonomy.group_by_category(papers)
        return papers
    
    def __daily_arxiv_update(self, topic: str):
        """
        Builds a list of formatted Discord messages summarising yesterday's papers for a topic.

        Each message is kept within the Discord character limit (CHAR_LIMIT). Papers are
        grouped by subtopic, with each subtopic rendered as a section containing paper
        titles, authors, and links. Subtopic sections that would exceed the character
        limit are truncated by removing papers (in groups of three lines) until they fit.

        Args:
            topic (str): The top-level ArXiv topic to generate an update for.

        Returns:
            list[str]: A list of message strings ready to be sent to a Discord channel.
        """
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
        """
        Starts the ArXivist bot using the provided Discord API token.

        This is a blocking call that runs until the bot is stopped.

        Args:
            token (str): The Discord bot token used to authenticate with the Discord API.
        """
        self.__bot.run(token)


# ----- Aux Functions -----

def log(message):
    """
    Prints a timestamped log message to stdout.

    Args:
        message (str): The message to log.
    """
    print(f'{datetime.now().strftime("%d/%m/%Y, %H:%M:%S")} - {message}.')

def load_channels_from_json(filepath: str):
    """
    Loads the channel-to-topics mapping from a JSON config file.

    The expected JSON structure is a dict mapping Discord channel names
    to lists of ArXiv topic strings, e.g.:
        { "ai-papers": ["Machine Learning", "Computer Vision"] }

    Args:
        filepath (str): Path to the JSON config file.

    Returns:
        dict: A mapping of channel names to their subscribed topic lists.
    """
    with open(filepath) as file:
        config = json.load(file)
    return config
