# DiffScript

DiffScript is a Python script designed for monitoring changes in JavaScript files on specified websites. It compares new and old versions of JS files, identifies new endpoints, and alerts via Telegram messaging for any changes. This script is particularly useful for web developers and security researchers who need to track updates or changes in the JavaScript used by websites.

## Installation

To run this script, you will need Python 3 and several dependencies:

Clone the Repository:

```
git clone https://github.com/xssdoctor/diffscript.git
cd diffscript
```

Install Dependencies:

```
pip install -r requirements.txt
```

Install Jsluice:

```
go install github.com/BishopFox/jsluice/cmd/jsluice@latest
```

## Usage

Before running the script, ensure you have a `starting_points.txt` file in your script directory with URLs you want to monitor.

Telegram Bot Setup:
Make sure to set up a [Telegram bot](https://core.telegram.org/bots) and obtain the `bot_token` and `chat_id` to use the messaging feature.
Once you have the bot token and chat ID, add the following lines to your `.bashrc` or `.zshrc` file:

```
export TELEGRAM_BOT_TOKEN="your-token-goes-here"
export TELEGRAM_CHAT_ID="your-chat-id-goes-here"
```

Run the Script:

```
python3 diffscript.py
```

Output:

The script will create directories for each monitored website, tracking changes in their JavaScript files.

## Features

- Monitors specified URLs for JavaScript file changes.
- Compares new and old versions of JS files.
- Identifies new endpoints.
- Sends alerts via Telegram for any updates or changes.

## Credits

This script is adapted from a gist by Greg Sunday, available at this link https://github.com/BishopFox/jsluice. The original concept and portions of the code were developed by Greg Sunday.

## Contributing

Contributions to this project are welcome. Please ensure to follow the existing coding style and add unit tests for any new or changed functionality.

## License

This project is open-source and available under the MIT License.
