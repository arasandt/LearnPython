import math

steering_list = [0.0, 0.5, 1, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 4.5, 5.0]
# adjust as needed
speed_list = [2.1, 2.4, 2.7, 2.9, 3.1, 3.3, 3.5, 3.7, 3.8, 3.9, 4.0]
# speed_list = [1.7, 2.0, 2.3, 2.5, 2.7, 2.9, 3.1, 3.3, 3.4, 3.5, 3.6]
# speed_list = [1.3, 1.6, 1.9, 2.1, 2.3, 2.5, 2.7, 2.9, 3.0, 3.1, 3.3]
steering_speed = list(zip(steering_list, speed_list[::-1]))


def get_speed_reward(row_steering, row_speed):
    global steering_speed

    speed_reward_factor = 0.33
    reward_base = 1
    reward = 1

    # not within limits then assign return default reward
    if row_steering >= max(steering_list) or row_speed > max(speed_list):
        pass
    elif row_steering < min(steering_list) or row_speed < min(speed_list):
        pass
    else:
        ideal_speed = row_speed
        for count in range(len(steering_speed) - 1):
            if steering_speed[count][0] <= row_steering < steering_speed[count + 1][0]:
                ideal_speed = steering_speed[count][1]
                break

        speed_diff = abs(row_speed - ideal_speed)

        if speed_diff > 0.2:
            if row_speed > ideal_speed:
                reward = reward_base + (speed_reward_factor / (speed_diff * 2))
            elif row_speed < ideal_speed:
                reward = reward_base + (speed_reward_factor / speed_diff)
        else:
            reward = reward_base + speed_reward_factor + 1

    return reward


def reward_function(params):

    if params["is_offtrack"]:
        reward = 0
    else:
        # Read input variables
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        heading = params["heading"]
        steps = params["steps"]
        speed = params["speed"]
        progress = params["progress"]
        steering = abs(params["steering_angle"])

        # Initialize the reward with typical values
        direction_reward = 1
        speed_reward = 1
        DIRECTION_THRESHOLD = 10
        ABS_STEERING_THRESHOLD = 25

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
            direction_reward *= 0.5

        ######## Reward #2 - STEERING REWARD ########
        if steering > ABS_STEERING_THRESHOLD:
            direction_reward *= 0.66

        ######## Reward #3 - FAST LANE REWARD ########
        if steps > 5:
            speed_reward = get_speed_reward(steering, speed)

        reward = direction_reward + speed_reward

        ######## Reward #4 - PROGRESS REWARD ########
        if steps > 5:
            reward *= progress * 1.66 / steps

    return float(reward)
