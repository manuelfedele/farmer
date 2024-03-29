# CircleCI Status

[![farmer](https://circleci.com/gh/manuelfedele/farmer.svg?style=shield&circle-token=4509c740c7399dff1c749c183c787dd31b72f199)](https://github.com/manuelfedele/farmer)

# Configuration

1) Create a virtual environment `virtualenv -p python3 venv`
2) Create an .env file (see .env.example)
3) Activate the virtual environment `source venv/bin/activate`
4) `pip install -r requirements.txt`
6) Run the bot :
   `python main.py`

Things to care about:

- The .env file takes precedence over the environment variables and the default values.
- The only differences between a live bot and a test bot are the APCA_API_KEY_ID and APCA_API_SECRET_KEY
- If you want to test the bot, you use the PAPER APCA_API_KEY_ID and APCA_API_SECRET_KEY
- The bot will only trade if it is in the market day (9:30-16:00 ET) if trading STOCKS

# Behavior

The bot uses the moving average to detect buy and sell signals. Pretty dumb. At the moment loses money.

# Next Steps

1) Refactor the code in order to follow the code style and make it more readable (SOLID principles)
2) Add more tests
3) Add more tests
4) Add more tests, because they are never enough
5) Create a StrategyFactory in order to use different strategies

# Deploy to production

[WIP]