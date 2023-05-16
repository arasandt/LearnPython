import math

min_speed, max_speed = 0.8, 3.8
max_steer = 30

speed_list = [i / 10 for i in range(int(min_speed * 10), int(max_speed * 10) + 1)]
steering_list = [i for i in range(0, max_steer + 2)]
steering_speed = list(zip(steering_list, speed_list[::-1]))
# print(steering_speed)


def get_speed_adj_reward(row_steering, row_speed):
    global steering_speed

    ideal_speed = steering_speed[-1][1]  # assign the lowest to ideal speed
    for count in range(len(steering_speed) - 1):
        if steering_speed[count][0] <= row_steering < steering_speed[count + 1][0]:
            ideal_speed = steering_speed[count][1]
            break
    # print(f"Current {row_speed} vs Ideal {ideal_speed}")

    speed_diff = abs(float(row_speed) - float(ideal_speed))
    # print("speed_diff", speed_diff)

    reward = 1 / math.pow(2, speed_diff)

    # print("reward", reward)
    return reward


def reward_function(params):

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        reward = 0
    else:
        # Read input variables
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        heading = params["heading"]
        steps = params["steps"]
        speed = params["speed"]
        progress = params["progress"]
        steering = params["steering_angle"]
        is_left = params["is_left_of_center"]

        # Initialize the reward with typical values
        direction_reward = 1
        # Depends on track for re:Invent 2019 its 45 and Canada its 45
        DIRECTION_THRESHOLD = 45

        ######## Check #2 - STEERING CHECK ########
        # For re:Invent 2019 track and Canada track, there is no need to turn right more than -5 degrees
        if steering <= -5:
            return 0.0
        steering = abs(steering)

        ######## Reward #1 - DIRECTION REWARD ########
        # Calculate the direction of the center line based
        next_point = waypoints[closest_waypoints[1]]
        prev_point = waypoints[closest_waypoints[0]]
        # Calculate the direction in radius, arctan2(dy, dx),
        track_direction = math.atan2(
            next_point[1] - prev_point[1], next_point[0] - prev_point[0]
        )
        # Convert to degree
        track_direction = math.degrees(track_direction)
        # Calculate the difference between the track direction and the heading directiorewardn of the car
        direction_diff = abs(track_direction - heading)
        if direction_diff > 180:
            direction_diff = 360 - direction_diff
        # Penalize the reward if the difference is too large
        if direction_diff > DIRECTION_THRESHOLD:
            direction_reward *= 0.66

        ######## Reward #2 - SPEED ADJUSTMENT REWARD ########
        speed_adj_reward = get_speed_adj_reward(steering, speed)

        ######## Reward #3 - KEEP LEFT REWARD ########
        # Depends on track for re:Invent 2019 its 0.2 and Canada its 0.3
        keep_left_reward = 1 if is_left else 0.2

        reward = direction_reward + speed_adj_reward + keep_left_reward

        ######## Reward #4 - PROGRESS REWARD ########
        if steps > 5:
            reward *= progress * 1.66 / steps

    return float(reward)
