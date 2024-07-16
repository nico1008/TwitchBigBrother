import os
from twitchio.ext import commands
from dotenv import load_dotenv
from transformers import pipeline
import psycopg2
from psycopg2 import Error

load_dotenv()

CLIENT_ID = os.getenv('TWITCH_CLIENT_ID')
CLIENT_SECRET = os.getenv('TWITCH_CLIENT_SECRET')
TOKEN = os.getenv('TWITCH_TOKEN')
NICK = 'nico_1008___'
PREFIX = '!'
INITIAL_CHANNELS = ['psp1g']

# Initialize the sentiment analysis pipeline
sentiment_pipeline = pipeline("sentiment-analysis")

# Connect to the PostgreSQL database
conn = psycopg2.connect(
    host=os.getenv('DB_HOST'),
    port=os.getenv('DB_PORT'),
    dbname=os.getenv('DB_NAME'),
    user=os.getenv('DB_USER'),
    password=os.getenv('DB_PASSWORD')
)
cur = conn.cursor()

class Bot(commands.Bot):

    def __init__(self):
        super().__init__(token=TOKEN, prefix=PREFIX, initial_channels=INITIAL_CHANNELS)
        self.messages = []

    async def event_ready(self):
        print(f'Logged in as | {self.nick}')

    async def event_message(self, message):
        if message.author is None:
            return

        username = message.author.name.lower()

        # Exclude bot messages and banned users
        if username == self.nick.lower() or "bot" in username or self.is_banned(username):
            return

        # Analyze sentiment of the message
        sentiment = sentiment_pipeline(message.content)[0]
        sentiment_label = sentiment['label']
        
        # Save sentiment data to the database
        self.save_sentiment_data(username, sentiment_label)

        # Optional: Print sentiment analysis
        print(f'{username}: {message.content} - Sentiment: {sentiment}')

        # Handle commands if needed
        await self.handle_commands(message)

    def is_banned(self, username):
        try:
            cur.execute("SELECT 1 FROM banlist WHERE username = %s", (username,))
            return cur.fetchone() is not None
        except Error as e:
            print(f"Database error in is_banned: {e}")
            conn.rollback()  # Rollback the transaction on error
            return False

    def save_sentiment_data(self, username, sentiment_label):
        try:
            cur.execute("SELECT positive, negative FROM user_sentiment WHERE username = %s", (username,))
            result = cur.fetchone()

            if result:
                positive, negative = result
                if sentiment_label == 'POSITIVE':
                    positive += 1
                else:
                    negative += 1
                cur.execute(
                    "UPDATE user_sentiment SET positive = %s, negative = %s WHERE username = %s",
                    (positive, negative, username)
                )
            else:
                positive = 1 if sentiment_label == 'POSITIVE' else 0
                negative = 1 if sentiment_label == 'NEGATIVE' else 0
                cur.execute(
                    "INSERT INTO user_sentiment (username, positive, negative) VALUES (%s, %s, %s)",
                    (username, positive, negative)
                )

            conn.commit()
        except Error as e:
            print(f"Database error in save_sentiment_data: {e}")
            conn.rollback()  # Rollback the transaction on error

    @commands.command(name='hello')
    async def hello(self, ctx):
        await ctx.send(f'Hello {ctx.author.name}!')

    @commands.command(name='score')
    async def score(self, ctx):
        username = ctx.author.name.lower()
        try:
            cur.execute("SELECT positive, negative FROM user_sentiment WHERE username = %s", (username,))
            result = cur.fetchone()

            if result:
                positive, negative = result
                await ctx.send(f'{ctx.author.name}, your positive score is {positive} and your negative score is {negative}.')
            else:
                await ctx.send(f'{ctx.author.name}, you have no sentiment data recorded.')
        except Error as e:
            print(f"Database error in score command: {e}")
            conn.rollback()  # Rollback the transaction on error

    @commands.command(name='ban')
    async def ban(self, ctx):
        if ctx.author.name.lower() == NICK.lower():  # Only allow the specific user to ban
            try:
                parts = ctx.message.content.split()
                if len(parts) < 2:
                    await ctx.send('Please specify a user to ban.')
                    return
                
                username_to_ban = parts[1].lower()
                if self.is_banned(username_to_ban):
                    await ctx.send(f'User {username_to_ban} is already banned.')
                    return

                cur.execute("INSERT INTO banlist (username) VALUES (%s)", (username_to_ban,))
                conn.commit()
                await ctx.send(f'User {username_to_ban} has been banned.')
            except Error as e:
                print(f"Database error in ban command: {e}")
                conn.rollback()  # Rollback the transaction on error
                await ctx.send(f'Error banning user {username_to_ban}.')
        else:
            await ctx.send('You do not have permission to use this command.')

    @commands.command(name='unban')
    async def unban(self, ctx):
        if ctx.author.name.lower() == NICK.lower():  # Only allow the specific user to unban
            try:
                parts = ctx.message.content.split()
                if len(parts) < 2:
                    await ctx.send('Please specify a user to unban.')
                    return
                
                username_to_unban = parts[1].lower()
                if not self.is_banned(username_to_unban):
                    await ctx.send(f'User {username_to_unban} is not banned.')
                    return

                cur.execute("DELETE FROM banlist WHERE username = %s", (username_to_unban,))
                conn.commit()
                await ctx.send(f'User {username_to_unban} has been unbanned.')
            except Error as e:
                print(f"Database error in unban command: {e}")
                conn.rollback()  # Rollback the transaction on error
                await ctx.send(f'Error unbanning user {username_to_unban}.')
        else:
            await ctx.send('You do not have permission to use this command.')

bot = Bot()
bot.run()

# Close the cursor and connection when done
cur.close()
conn.close()