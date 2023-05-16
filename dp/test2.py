import pandas as pd
import math
from rf2 import get_speed_adj_reward

pd.set_option("display.max_columns", None)

steering = [i for i in range(0, 31)]
speed = [float(i / 10) for i in range(8, 41, 2)]
data = []
for st in steering:
    for sp in speed:
        data.append((st, sp))
# print(data)
df = pd.DataFrame(data, columns=["steering", "speed"])


def speed_reward(row):
    row_steering, row_speed, row_reward = row[0], row[1], row[2]
    return get_speed_adj_reward(row_steering, row_speed)


df["basereward"] = 1
df["reward"] = df.apply(speed_reward, axis=1)

df.to_csv("data2.csv", index=False)
