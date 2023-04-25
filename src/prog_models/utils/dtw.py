import numpy as np
from dtaidistance import *


def helperDTW(s, t):
    matrix = np.zeros((len(s)+1, len(t)+1))
    for i in range(len(s)+1):
        for j in range(len(t)+1):
            matrix[i, j] = np.inf
    matrix[0, 0] = 0
    for i in range(1, len(s)+1):
        for j in range(1, len(t)+1):
            dist = abs(s[i-1] - t[j-1])
            result = np.min([matrix[i-1, j],
                            matrix[i, j-1],
                            matrix[i-1, j-1]])
            matrix[i, j] = dist + result
    return matrix[len(s), len(t)]


first = [{'x': 2.83}, {'x': 22.782915491311915}, {'x': 55.348408177738214}, {'x': 67.97548348505318}, 
         {'x': 78.16253899306928}, {'x': 85.86342516495017}, {'x': 91.24039201850137}, {'x': 93.95951760932972}, 
         {'x': 94.25080555274945}, {'x': 92.10808905052906}, {'x': 87.41211393336862}, {'x': 80.39323799824747}, 
         {'x': 70.86501749985752}, {'x': 59.013290213428725}, {'x': 27.812270186219685}, {'x': 8.539606731718017}, 
         {'x': -13.173964185590503}]

holder = []

for i in first:
    holder.append(i.get('x'))

first = holder

second = [{'x': 2.83}, {'x': 22.80837311477341}, {'x': 40.281912963742215}, {'x': 55.42398315943566}, 
          {'x': 68.07057685550954}, {'x': 78.20806209327021}, {'x': 85.81739091324083}, {'x': 90.90419049364598}, 
          {'x': 93.55397297905536}, {'x': 93.82329042643599}, {'x': 91.55063631253319}, {'x': 86.87458308281157}, 
          {'x': 79.8227380277596}, {'x': 70.25684320147167}, {'x': 58.29644667735673}, {'x': 43.73967557742929}, 
          {'x': 26.834112707928966}, {'x': 7.456760394259649}, {'x': -14.452760996049799}]

holder = []

for i in second: 
    holder.append(i.get('x'))

second = holder

result = helperDTW(first, second)

print(result)



a = [1, 2, 3]
b = [2, 2, 2, 3, 4]

        
dtw_i = 0

for dim in range(1, max(len(a), len(b)) + 1):
    dtw_i += dtw.distance(a[:dim], b[:dim])

print(dtw_i)
