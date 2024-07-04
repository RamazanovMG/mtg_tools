import pandas as pd
import sys
import re

# Usage:
# Display all: python leaderboard_display.py
# Boros decks: python display.py -a boros
# Display all for explorer: python leaderboard_display.py explorer
# Display most recent players: python leaderboard_display.py last 10
# Display all records between dates : python leaderboard_display.py timeframe 03-05
# Display records starting with date: python leaderboard_display.py timeframe 03-
# all combinations work


def sort_by_wr(df):
    df.loc[:, 'wr'] = df['wr'].fillna('0%')
    df.loc[:, 'wr'] = df['wr'].str.rstrip('%').astype('float')
    df = df.sort_values(by=['wr', 'date'], ascending=[False, True])
    df.loc[:, 'wr'] = df['wr'].apply(lambda x: f'{x:.1f}%')
    new_names = {'standard_bo1': 's bo1', 'standard_bo3': 's bo3',
                 'explorer_bo1': 'e bo1', 'explorer_bo3': 'e bo3',
                 'alchemy_bo1': 'a bo1', 'alchemy_bo3': 'a bo3',
                 'historic_bo1': 'h bo1', 'historic_bo3': 'h bo3',
                 'timeless_bo1': 't bo1', 'timeless_bo3': 't bo3',
                 }
    for key, value in new_names.items():
        df['format'] = df['format'].replace(key, value)
    df['name'] = df['name'].apply(lambda x: x[:15])  # обрезаю длинные имена
    df['archetype'] = df['archetype'].apply(lambda x: x[:20])  # и архетипы
    return df


formats_unspecified = {'standard', 'explorer', 'alchemy', 'historic', 'timeless'}
suffixes = {'bo1', 'bo3'}
formats = set()
for f in formats_unspecified:
    for suffix in suffixes:
        formats.add(f + '_' + suffix)
valid_formats = formats.copy()

last = None
timeframe = None
archetype = None
top = None
formats_from_console = sys.argv[1:]
freqs = False
months = None
if 'freqs' in sys.argv:
    freqs = True
    formats_from_console = []
if 'last' in sys.argv:
    index = sys.argv.index('last')
    last = int(sys.argv[index + 1])
    i = formats_from_console.index('last')
    formats_from_console.pop(i)
    formats_from_console.pop(i)
if 'months' in sys.argv:
    index = sys.argv.index('months')
    months = sys.argv[index + 1]
    i = formats_from_console.index('months')
    formats_from_console.pop(i)
    formats_from_console.pop(i)
if 'top' in sys.argv:
    index = sys.argv.index('top')
    top = int(sys.argv[index + 1])
    i = formats_from_console.index('top')
    formats_from_console.pop(i)
    formats_from_console.pop(i)
if 'timeframe' in sys.argv:
    index = sys.argv.index('timeframe')
    timeframe = sys.argv[index + 1]
    i = formats_from_console.index('timeframe')
    formats_from_console.pop(i)
    formats_from_console.pop(i)
if '-a' in sys.argv:
    index = sys.argv.index('-a')
    archetype = sys.argv[index + 1]
    i = formats_from_console.index('-a')
    formats_from_console.pop(i)
    formats_from_console.pop(i)

if not formats_from_console:
    formats_from_console = formats
else:
    formats = set()

for arg in formats_from_console:
    if arg in suffixes:
        for f in formats_unspecified:
            formats.add(f + '_' + arg)
    elif arg in formats_unspecified:
        for suffix in suffixes:
            formats.add(arg + '_' + suffix)
    elif arg in valid_formats:
        formats.add(arg)
    else:
        print(f'Typo in \'{arg}\'')
        sys.exit(1)


df_original = pd.read_csv('leaderboard.csv')
df = df_original[df_original['format'].isin(formats)]
dates = None
if not months:
    month = re.match(r'(\w+)', df['date'].iloc[-1]).group(1)
    months = [month]
else:
    months = months.split(' ')
# df = df[df['date'].astype(str).str.startswith(month)]
df = df[df['date'].apply(lambda x: any(x.startswith(m) for m in months))]
if freqs:
    existing_formats = set(df['format'].unique())
    df = df['format'].value_counts()
    f = set(formats)
    missing_formats = f - existing_formats
    for mf in missing_formats:
        df.loc[mf] = 0
    print(df.to_string)
    exit(0)
if timeframe:
    match = re.match(r'(\d*)-(\d*)', timeframe)
    first_date = match.group(1) if match.group(1) else '01'
    last_date = match.group(2) if match.group(2) else '31'
    first_date_int = int(first_date)
    last_date_int = int(last_date)
    dates = set()
    for i in range(first_date_int, last_date_int + 1):
        dates.add(month + ' ' + str(i).zfill(2))

if last:
    df = df.tail(last)
if archetype:
    df = df[df['archetype'].str.contains(archetype, case=False)]

df = sort_by_wr(df)
# df = df[df['date'].astype(str).str.startswith(month)]
if dates:
    df = df[df['date'].isin(dates)]
if top:
    df = df.head(top)
df = df[['link', 'archetype', 'format', 'wr', 'date']]
print(df.to_string(index=False))
