from bs4 import BeautifulSoup
from selenium import webdriver
import time
import csv
import os
import pandas as pd
import sys
from datetime import datetime

# Usage 1 (parse all formats): python leaderboard_parse.py
# Usage 2 (parse specific formats): python leaderboard_parse.py standard explorer historic


def update_journal(url, f, bo, zero_players_found, timeout, counter_new_players):
    print(f'{f.capitalize()} {bo}.', end='\t')
    driver.get(url)
    time.sleep(timeout)
    html_content = driver.page_source

    soup = BeautifulSoup(html_content, 'html.parser')
    class_prefix = 'MythicAttainmentOverview__Content'
    leaderboard = soup.select(f'[class^="{class_prefix}"]')[0]
    parsed_leaderbard = leaderboard.find_all(
        class_=lambda x: x and x.startswith('MythicLeaderboardItem__LeaderboardItem'))

    counter = 0
    counter_new_entry = 0
    for item in parsed_leaderbard:
        link = ''
        if 'href' in item.attrs:
            link = 'https://mtga.untapped.gg' + item['href']
        else:
            # Looking at an empty cell
            break

        winrate = item.find(class_=lambda x: x and x.startswith('MythicLeaderboardItem__Winrate')).text

        player_name = item.find(class_=lambda x: x and x.startswith('MythicLeaderboardItem__PlayerName')).text

        archetype = item.find(class_=lambda x: x and x.startswith('MythicLeaderboardItem__ArchetypeName')).text

        current_date = datetime.now()

        # [format, name, link, archetype, winrate, date]
        row = [f'{f}_{bo}', player_name, link, archetype, winrate, current_date.strftime('%B %d')]

        df = pd.read_csv('leaderboard.csv')
        new_row = pd.DataFrame([row], columns=df.columns)
        if row[2] not in df['link'].values:
            df = pd.concat([df, new_row], ignore_index=True)
            counter_new_entry += 1

        df.to_csv('leaderboard.csv', index=False)

        counter += 1

    if counter == 0:
        format_string = f'{f} {bo}'
        zero_players_found.append(format_string)
    print(f'Completed.\t{counter} players found ({counter_new_entry} new)')
    return counter_new_players + counter_new_entry


options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--ignore-certificate-errors')
options.add_argument('--disable-quic')
options.add_argument('log-level=3')
driver = webdriver.Chrome(options=options)

formats = ['standard', 'explorer', 'alchemy', 'historic', 'timeless']
filename = 'leaderboard.csv'
columns = ['format', 'name', 'link', 'archetype', 'winrate', 'date']
zero_players_found = []
counter_new_players = 0
def is_integer(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


timeout = 10
if len(sys.argv) == 2 and is_integer(sys.argv[1]):
    timeout = int(sys.argv[1])
elif len(sys.argv) > 1:
    if any(f not in formats for f in sys.argv[1:]):
        print('Typo')
        driver.quit()
        sys.exit(1)
    formats = sys.argv[1:]

if not os.path.exists(filename):
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(columns)

for f in formats:
    url_bo1 = f'https://mtga.untapped.gg/meta?format={f}'
    counter_new_players = update_journal(url_bo1, f, 'bo1', zero_players_found, timeout, counter_new_players)
    url_bo3 = url_bo1 + '&wincon=bo3'
    counter_new_players = update_journal(url_bo3, f, 'bo3', zero_players_found, timeout, counter_new_players)
print(f'\t{counter_new_players} new entries')

print(f'\nNo players found for the following formats:')
for zpf in zero_players_found:
    print(f'\t {zpf.capitalize()}')

driver.quit()

print(f"Finished parsing at {datetime.now().strftime('%H:%M:%S')}")
