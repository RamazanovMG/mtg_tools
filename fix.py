import pandas as pd
import sys

# Usage: fix.py incorrect_month correct_month

df = pd.read_csv('leaderboard.csv')
incorrect_month = sys.argv[1]
correct_month = sys.argv[2]
df['date'] = df['date'].apply(lambda x: correct_month if x == incorrect_month else x)
df.to_csv('leaderboard.csv', index=False)
print(f'{incorrect_month} changed to {correct_month}')