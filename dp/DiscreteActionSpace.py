import pandas as pd
import itertools

MAX_STEERING_LEFT = 30
MAX_STEERING_RIGHT = -30
MAX_STEERING_LEFT_CUTOFF = 30
MAX_STEERING_RIGHT_CUTOFF = -22.5
MIN_SPEED, MAX_SPEED = 1.2, 3.2
SPEED_GRANULARITY = 0.2
STEERING_GRANULARITY = 2.5


def get_steering_list():
    # print(
    #     int(-MAX_STEERING_RIGHT * 10),
    #     int(MAX_STEERING_LEFT * 10 + 1),
    #     int(STEERING_GRANULARITY * 10),
    # )
    steering_list = [
        i / 10
        for i in range(
            int(MAX_STEERING_RIGHT * 10),
            int(MAX_STEERING_LEFT * 10 + 1),
            int(STEERING_GRANULARITY * 10),
        )
    ]
    if MAX_STEERING_RIGHT not in steering_list:
        steering_list.insert(0, float(MAX_STEERING_RIGHT))
    if MAX_STEERING_LEFT not in steering_list:
        steering_list.append(float(MAX_STEERING_LEFT))
    if MAX_STEERING_RIGHT_CUTOFF not in steering_list:
        steering_list.insert(0, float(MAX_STEERING_RIGHT_CUTOFF))
    if MAX_STEERING_LEFT_CUTOFF not in steering_list:
        steering_list.append(float(MAX_STEERING_LEFT_CUTOFF))
    # print(steering_list)
    return steering_list


def get_speed_list():
    # print(
    #     int(-MIN_SPEED * 10),
    #     int(MAX_SPEED * 10 + 1),
    #     int(SPEED_GRANULARITY * 10),
    # )
    speed_list = [
        i / 10
        for i in range(
            int(MIN_SPEED * 10),
            int(MAX_SPEED * 10 + 1),
            int(SPEED_GRANULARITY * 10),
        )
    ]
    if MIN_SPEED not in speed_list:
        speed_list.append(float(MAX_STEERING_LEFT))
    if MAX_SPEED not in speed_list:
        speed_list.insert(0, float(MAX_SPEED))
    # print(speed_list)
    return speed_list


def generate_action_space():
    steering_list = get_steering_list()
    speed_list = get_speed_list()
    final_list = []
    for element in itertools.product(*[steering_list, speed_list]):
        if MAX_STEERING_RIGHT_CUTOFF <= element[0] <= MAX_STEERING_LEFT_CUTOFF:
            final_list.append(element)
    # print(final_list)

    df = pd.DataFrame(final_list, columns=["steering", "speed"])
    # print(df.head())
    gfg_csv_data = df.to_csv("DiscreteActionSpace.csv", index=False)


generate_action_space()
