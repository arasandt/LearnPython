import pandas as pd
import math

pd.set_option("display.max_columns", None)

steering = [(i / 2) for i in range(12) if (i / 2) <= 5]
speed = [(i / 4) for i in range(7, 50) if 1.2 < (i / 4) <= 4]
print(steering[:11], len(steering))
print(speed[:10], len(speed))
steering = steering[:11]
speed = speed[:10]
data = zip(steering[:10], speed[:10])
data = []
for st in steering[:10]:
    for sp in speed[:10]:
        data.append((st, sp))

df = pd.DataFrame(data, columns=["steering", "speed"])
# print(df.tail())


def apply_reward(row):
    # global speed
    # global steering

    # steering_list = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    steering_list = [0.0, 0.5, 1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    speed_list = [1.8, 2.1, 2.4, 2.7, 2.9, 3.1, 3.3, 3.5, 3.7, 3.8, 3.9, 4.0]

    speed_reward_factor = 1.25

    row_steering = row[0]
    # row_steering = 0.5
    row_speed = row[1]
    # row_speed = 3.99
    row_reward = row[2]
    # print("row_steering", row_steering)
    # print("row_speed", row_speed)
    # print(row_reward)
    reward = 1

    if row_steering > max(steering_list) or row_speed > max(speed_list):
        # reward = speed_reward_factor / len(speed_list)
        pass
    elif row_steering < min(steering_list) or row_speed < min(speed_list):
        # reward = speed_reward_factor / len(speed_list)
        pass
    else:
        steering_index = len(steering_list)
        for count in range(len(steering_list) - 1):
            if steering_list[count] <= row_steering < steering_list[count + 1]:
                steering_index = count
                break

        # print("steering_index", steering_index)

        less_speed, ideal_speed, more_speed = (
            speed_list[: -steering_index - 1],
            [speed_list[-steering_index - 1]],
            speed_list[len(speed_list) - steering_index :],
        )
        # print(less_speed)
        # print(ideal_speed)
        # print(more_speed)

        speed_reward = []
        count = 1
        reward_base = 1
        for i in less_speed[::-1]:
            r = speed_reward_factor - (count * speed_reward_factor / len(speed_list))
            speed_reward.append((i, reward_base + r))
            count += 1
        for i in ideal_speed:
            speed_reward.append((i, reward_base + speed_reward_factor))
        count = 1
        for i in more_speed:
            r = (
                speed_reward_factor
                - (count * speed_reward_factor / len(speed_list)) * 2
            )

            speed_reward.append((i, reward_base + r))
            count += 1

        speed_reward.sort(key=lambda key: key[0])
        # print(speed_reward)

        for count in range(len(speed_reward) - 1):
            if speed_reward[count][0] <= row_speed < speed_reward[count + 1][0]:
                reward = speed_reward[count][1]
                break
        if row_speed == speed_reward[-1][0]:
            reward = speed_reward[-1][1]
    # print("reward", reward)
    # 0 / 0
    return reward * row_reward


def apply_speed_reward(row):

    speed_reward_factor = 0.33
    reward_base = 1
    steering_list = [0.0, 0.5, 1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
    speed_list = [2.1, 2.4, 2.7, 2.9, 3.1, 3.3, 3.5, 3.7, 3.8, 3.9, 4.0]
    # print(len(steering_list))
    # print(len(speed_list))

    steering_speed = list(zip(steering_list, speed_list[::-1]))
    # print(steering_speed)

    row_steering, row_speed, row_reward = row[0], row[1], row[2]
    # row_steering = 0.5
    # row_speed = 2.7
    # print("row_steering", row_steering)
    # print("row_speed", row_speed)
    # print(row_reward)

    reward = 1
    if row_steering >= max(steering_list) or row_speed > max(speed_list):
        # print("beyond max")
        pass
    elif row_steering < min(steering_list) or row_speed < min(speed_list):
        # print("beyond min")
        pass
    else:
        # print("within range")
        ideal_speed = row_speed
        for count in range(len(steering_speed) - 1):
            if steering_speed[count][0] <= row_steering < steering_speed[count + 1][0]:
                ideal_speed = steering_speed[count][1]
                break
        # print("ideal_speed", ideal_speed)

        speed_diff = abs(row_speed - ideal_speed)
        # print(speed_diff)

        if speed_diff > 0.2:
            if row_speed > ideal_speed:
                # print("speed is more")
                reward = reward_base + (speed_reward_factor / (speed_diff * 2))
            elif row_speed < ideal_speed:
                # print("speed is less")
                reward = reward_base + (speed_reward_factor / speed_diff)
        else:
            reward = reward_base + speed_reward_factor + 1

    # print(reward)
    # 0 / 0
    return reward


df["basereward"] = 1
df["reward"] = df.apply(apply_speed_reward, axis=1)

df.to_csv("data1.csv", index=False)
