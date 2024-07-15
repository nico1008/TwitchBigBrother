import os
from twitchio.ext import commands
from dotenv import load_dotenv
from transformers import pipeline

load_dotenv()

CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TOKEN = os.getenv('TWITCH_TOKEN')
NICK = 'nico_1008___'
PREFIX = '!'
INITIAL_CHANNELS = ['nico_1008___', 'jokerdtv']

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TOKEN, prefix=PREFIX, initial_channels=INITIAL_CHANNELS)
        self.messages = []

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):

        # Analyze sentiment of the message
        sentiment = sentiment_pipeline(message.content)[0]

        # Store message with sentiment analysis
        self.messages.append({
            'author': message.author.name,
            'content': message.content,
            'timestamp': message.timestamp,
            'sentiment': sentiment
        })

        # Print sentiment analysis 
        print(f'{message.author.name}: {message.content} - Sentiment: {sentiment}')

        # Handle commands if needed
        await self.handle_commands(message)

    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')

    # Method to get stored messages
    def get_messages(self):
        return self.messages

bot = Bot()
bot.run()