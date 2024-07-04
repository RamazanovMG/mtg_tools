import itertools
import numpy as np
from collections import Counter

# colors = ['w', 'u', 'b', 'r', 'g']
colors = ['g', 'r']

basics = tuple((tuple(i)) for i in colors)
shocklands = tuple(itertools.combinations(colors, 2))
triomes = tuple(itertools.combinations(colors, 3))

# triomes_count in 10
# all basics at least once
# ratio: 8:0:4:14:18 for wubrg
# lands_count == 27

current = []
best = None
best_score = float('inf')


def evaluate(lands, desired_wubrg_ratio, d=None):
    if not d:
        d = {'w': 0, 'u': 0, 'b': 0, 'r': 0, 'g': 0}
    for land in lands:
        for color in land:
            d[color] += 1

    target_ratio = np.array(desired_wubrg_ratio)

    # Normalize the target ratio
    target_ratio = target_ratio / np.sum(target_ratio)

    numbers = [d['w'], d['u'], d['b'], d['r'], d['g']]

    # Normalize the input numbers
    numbers = np.array(numbers) / np.sum(numbers)

    # Calculate the Euclidean distance
    distance = np.linalg.norm(numbers - target_ratio)

    return distance


best_manabase = None
best_distance = float('inf')
#
# lands = basics + shocklands + triomes
#
# for current_lands in itertools.combinations_with_replacement(lands, 26):
#     counter = Counter(current_lands)
#     if any(count > 4 and key not in basics for key, count in counter.items()):
#         continue  # Skip this iteration
#     result = evaluate(current_lands, [33, 31, 0, 0, 14])
#     if result < best_distance:
#         best_distance = result
#         best_manabase = current_lands
#         print(best_distance)
#         print(best_manabase)

default_dict = {'w': 0, 'u': 0, 'b': 0, 'r': 2, 'g': 4}
ratio = [0, 0, 0, 12, 10]
lands = basics
for current_lands in itertools.combinations_with_replacement(lands, 13):
    if not {('r',), ('g',)}.issubset(current_lands):
        continue
    counter = Counter(current_lands)
    result = evaluate(current_lands, ratio, d=default_dict)
    if result < best_distance:
        best_distance = result
        best_manabase = current_lands
        print(best_distance)
        print(best_manabase)
