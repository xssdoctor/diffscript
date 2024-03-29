#!/usr/bin/env python3

import requests
from bs4 import BeautifulSoup
import re
import subprocess
from aiohttp import ClientSession
import json
import asyncio
from urllib import parse
from urllib.parse import urljoin
import os

TELEGRAM_CHAT_ID = ''
TELEGRAM_BOT_TOKEN = ''

cwd = os.getcwd()

if not os.environ.get('TELEGRAM_BOT_TOKEN'):
    print('[!] No Telegram bot token found! Consider adding "export TELEGRAM_BOT_TOKEN=\'<your-token>\'" to your .bashrc/.zshrc!')
    TELEGRAM_BOT_TOKEN = input('Enter one here: ')
else:
    TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')

if not os.environ.get('TELEGRAM_CHAT_ID'):
    print('[!] No Telegram chat ID found! Consider adding "export TELEGRAM_CHAT_ID=\'<your-chatID>\'" to your .bashrc/.zshrc!')
    TELEGRAM_CHAT_ID = input('Enter one here: ')
else:
    TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')


def get_starting_points():
    endpoints = []
    with open(os.path.join(cwd, 'starting_points.txt'), 'r') as infile:
        for line in infile.readlines():
            endpoints.append(line.strip())
    return endpoints


def update_working_dir(starting_point):
    regex = re.compile(r'(https?:\/\/)([a-z0-9\-\.]+)(\/.*)?')
    subfolder = regex.findall(starting_point)[0][1]
    if not os.path.exists(os.path.join(cwd, subfolder)):
        os.makedirs(os.path.join(cwd, subfolder))
    return os.path.join(cwd, subfolder)


def get_old_urls(working_dir) -> list:
    old_dir = os.path.join(working_dir, 'old')
    # list all files in this directory
    return os.listdir(old_dir)


def updateFolders(working_dir):
    if os.path.exists(working_dir + '/new'):
        # delete the old folder and everything in it
        if os.path.exists(working_dir + '/old'):
            os.system('rm -rf ' + working_dir + '/old')
        # rename the folder /new to /old and rename old to older
        os.rename(working_dir + '/new', working_dir + '/old')
        os.makedirs(working_dir + '/new')
        return True
    else:
        os.makedirs(working_dir + '/new')
        return False


async def download_urls(inputFile, working_dir):
    try:
        async with ClientSession() as session:
            async with session.get(inputFile) as response:
                content = await response.read()
                basename = inputFile.split('/')[-1]
                with open(os.path.join(working_dir, 'new', basename), 'wb') as outfile:
                    outfile.write(content)
    except:
        return 'download_urls failed to process'


async def fetch_js_urls_from_website(html, target_url, working_dir):
    try:
        jsfiles = []
        soup = BeautifulSoup(html, 'html.parser')
        script_tags = soup.find_all('script')
        js_links = [script.get('src')
                    for script in script_tags if script.get('src')]
        tasks = []
        for js_link in js_links:
            full_url = urljoin(target_url, js_link) if not js_link.startswith(
                'http') else js_link
            if '.js' in full_url:
                jsfiles.append(full_url)
                # Collect coroutine objects
                tasks.append(download_urls(full_url, working_dir))
        await asyncio.gather(*tasks)  # Run all download tasks concurrently
        return jsfiles
    except:
        return 'fetch_js_urls_from_website failed to process'


def get_new_urls(working_dir):
    new_dir = os.path.join(working_dir, 'new')
    # list all files in this directory
    return os.listdir(new_dir)


def fetch_urls(working_dir, endpoints):
    try:
        jsFiles = get_new_urls(working_dir)
        for jsfile in jsFiles:
            try:
                process = subprocess.Popen(
                    ['jsluice', 'urls', os.path.join(working_dir, 'new', jsfile)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                stdout, stderr = process.communicate()
                for endpoint in stdout.decode().split('\n'):
                    if endpoint:
                        endpoints.add(endpoint.strip())
            except Exception as e:
                return f'Exception caught in "fetch_urls": {e}'
    except:
        return 'fetch_urls failed process'


def save_endpoints(working_dir, endpoints):
    with open(os.path.join(working_dir, 'new', 'endpoints.txt'), 'w') as outfile:
        outfile.write('\n'.join(endpoints))
    return endpoints


def load_old_endpoints(working_dir):
    with open(os.path.join(working_dir, 'old', 'endpoints.txt'), 'r') as infile:
        return infile.read().split('\n')


def load_new_endpoints(working_dir):
    with open(os.path.join(working_dir, 'new', 'endpoints.txt'), 'r') as infile:
        return infile.read().split('\n')


def send_telegram_message(message):
    message = parse.quote(message)
    send_text = f'https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text={message}'
    resp = requests.get(send_text)
    return resp.json()


async def get_js_from_endpoints(endpoints, working_dir):
    try:
        working_dir = working_dir.split('/')[-1]
        tasks = []
        for endpoint in endpoints:
            endpoint = json.loads(endpoint)
            endpoint = endpoint['url']
            if endpoint.endswith('.js'):
                if not endpoint.startswith('/'):
                    endpoint = f'https://{working_dir}/{endpoint}'
                    tasks.append(download_urls(endpoint, working_dir))
        await asyncio.gather(*tasks)
    except:
        return 'get_js_from_endpoints failed to process'


async def main():
    starting_points = get_starting_points()
    for startingpoint in starting_points:
        if startingpoint:
            working_dir = update_working_dir(startingpoint)
            oldAndNew = updateFolders(working_dir)
            # setup lists for sending to telegram - keeps it at 1 message per target, per list
            telegram_urls = []
            telegram_endpoints = []
            if oldAndNew:
                html = requests.get(startingpoint).text
                await fetch_js_urls_from_website(
                    html, startingpoint, working_dir)
                endpoints = set()
                fetch_urls(working_dir, endpoints)
                await get_js_from_endpoints(endpoints, working_dir)
                fetch_urls(working_dir, endpoints)
                save_endpoints(working_dir, endpoints)
                oldUrls = sorted(get_old_urls(working_dir))
                newUrls = sorted(get_new_urls(working_dir))
                for newUrl in newUrls:
                    if newUrl not in oldUrls:
                        telegram_urls.append((newUrl, working_dir))
                oldEndpoints = sorted(load_old_endpoints(working_dir))
                newEndpoints = sorted(load_new_endpoints(working_dir))
                for newEndpoint in newEndpoints:
                    if newEndpoint and newEndpoint not in oldEndpoints:
                        telegram_endpoints.append(newEndpoint)
            else:
                html = requests.get(startingpoint).text
                await fetch_js_urls_from_website(
                    html, startingpoint, working_dir)
                endpoints = set()
                fetch_urls(working_dir, endpoints)
                await get_js_from_endpoints(endpoints, working_dir)
                fetch_urls(working_dir, endpoints)
                save_endpoints(working_dir, endpoints)

            # send the alert after the targets are processed
            if telegram_urls:
                send_telegram_message(f'New JS Files:\n {telegram_urls}')
            if telegram_endpoints:
                send_telegram_message(f'New Endpoints:\n {telegram_endpoints}')


if __name__ == "__main__":
    asyncio.run(main())
