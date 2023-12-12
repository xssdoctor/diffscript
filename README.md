DiffScript

DiffScript is a Python script designed for monitoring changes in JavaScript files on specified websites. It compares new and old versions of JS files, identifies new endpoints, and alerts via Telegram messaging for any changes. This script is particularly useful for web developers and security researchers who need to track updates or changes in the JavaScript used by websites.

Installation

To run this script, you will need Python 3 and several dependencies:

Clone the Repository:
bash
Copy code
git clone https://github.com/your-github-username/diffscript.git
cd diffscript
Install Dependencies:
Copy code
pip install requests beautifulsoup4 aiohttp
Usage

Before running the script, ensure you have a starting_points.txt file in your script directory with URLs you want to monitor.

Run the Script:
Copy code
python3 diffscript.py
Telegram Bot Setup:
Make sure to set up a Telegram bot and obtain the bot_token and chat_id to use the messaging feature.
Output:
The script will create directories for each monitored website, tracking changes in their JavaScript files.
Features

Monitors specified URLs for JavaScript file changes.
Compares new and old versions of JS files.
Identifies new endpoints.
Sends alerts via Telegram for any updates or changes.
Credits

This script is adapted from a gist by Greg Sunday, available at this link. The original concept and portions of the code were developed by Greg Sunday.

Contributing

Contributions to this project are welcome. Please ensure to follow the existing coding style and add unit tests for any new or changed functionality.

License

This project is open-source and available under the MIT License.
