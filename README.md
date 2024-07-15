# TwitchSentiment

TwitchSentiment is a Python application that analyzes the sentiment of messages in Twitch chat in real-time using machine learning models and stores the sentiment analysis results in a PostgreSQL database. It also provides functionality to manage a banlist of users.

## Features

- Real-time sentiment analysis of Twitch chat messages.
- Integration with PostgreSQL database to store sentiment analysis results.
- Commands to ban and unban users from the chat based on specified criteria.
- Command to check a user's positive and negative sentiment scores.

## Requirements

- Python 3.6+
- Required Python packages: twitchio, transformers, psycopg2-binary, python-dotenv

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/TwitchSentiment.git
   cd TwitchSentiment
