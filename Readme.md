# Configuration
1) Create a virtual environment and activate it.
2) `pip install -r requirements.txt`
3) Setup .env file (see .env.example)
4) Run the bot :
    `python main.py`

Things to care about:
 - The .env file takes precedence over the environment variables and the default values.
 - The only differences between a live bot and a test bot are the APCA_API_KEY_ID and APCA_API_SECRET_KEY
 - If you want to test the bot, you use the PAPER APCA_API_KEY_ID and APCA_API_SECRET_KEY
 - The bot will only trade if it is in the market day (9:30-16:00 ET)
 - Use SAVE_CONFIG=True to save the config file to disk and restart the bot from a previous state