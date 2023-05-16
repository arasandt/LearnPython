# Final - looks a difficult track. with 2.8, never reached 100% completion even after 3.5 hours. reached only 85% completion. better to do speed 2.6. May be increase hours to 6 hours.

import math

# 2019 Qualifier Track
# action space steering limit 30 to -15.
# training time 4 hours. May be try 6 hours.
# Minimum seconds during test 10.337 (clone gave 11.4)
DIRECTION_THRESHOLD = 10
ABS_STEERING_THRESHOLD = 15
MIN_SPEED, MAX_SPEED = 1.2, 2.6
# 2019 Qualifier Track

# Lars Loop Final Track
# training time 4-6 hours. Try 6 hours.
# Minimum seconds during test XX.XXXX.
# DIRECTION_THRESHOLD = 10
# ABS_STEERING_THRESHOLD = 20
# MIN_SPEED, MAX_SPEED = 1, 2.6
# Lars Loop Final Track


def direction_reward_fn(waypoints, closest_waypoints, heading):
    direction_reward = 1

    # Calculate the direction of the center line based
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]
    # Calculate the direction in radius, arctan2(dy, dx),
    track_direction = math.atan2(
        next_point[1] - prev_point[1], next_point[0] - prev_point[0]
    )
    # Convert to degree
    track_direction = math.degrees(track_direction)
    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff
    # Penalize the reward if the difference is too large
    if direction_diff > DIRECTION_THRESHOLD:
        direction_reward *= 0.66
    return direction_reward


def steering_reward_fn(reward, steering):
    steering_reward = 1

    if steering > ABS_STEERING_THRESHOLD:
        steering_reward = 0.66

    return reward + steering_reward


def fast_speed_reward_fn(reward, speed, steering, steps):
    speed_threshold_1 = MAX_SPEED * 0.85
    speed_threshold_2 = MAX_SPEED * 0.65
    steering_threshhold_1 = 2
    steering_threshhold_2 = 5
    speed_reward = 0

    if steps > 5 and speed <= MAX_SPEED:
        speed_reward = 1
        if steering <= steering_threshhold_1 and speed >= speed_threshold_1:
            speed_reward += speed / MAX_SPEED
            speed_reward *= 0.83
        elif (
            steering <= steering_threshhold_2
            and speed_threshold_2 <= speed < speed_threshold_1
        ):
            speed_reward += speed / speed_threshold_1
            speed_reward *= 0.66
    return reward + speed_reward


def slow_turn_reward_fn(reward, speed, steering, steps):
    speed_threshold = MIN_SPEED * 1.25
    steering_threshhold = 25
    slow_reward = 0

    if steps > 5 and speed >= MIN_SPEED:
        slow_reward = 1
        if steering >= steering_threshhold and speed <= speed_threshold:
            slow_reward += MIN_SPEED / speed
            slow_reward *= 0.66
    return reward + slow_reward


def progress_reward_fn(reward, progress, steps):
    if steps > 5:  # and not (steps % 1):
        progress_reward = 1 + progress / steps
        reward *= progress_reward
    return reward


def lane_reward_fn(reward, steering_angle, is_left):
    steering_threshhold_2 = 5
    lane_reward = 0

    if steering_angle > steering_threshhold_2 and is_left:
        lane_reward += 0.33

    if (steering_angle <= -22.5 and not is_left) or (
        steering_angle >= 22.5 and is_left
    ):
        lane_reward += 0.66
    return reward + lane_reward


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
        is_left = params["is_left_of_center"]
        steering_angle = params["steering_angle"]
        steering = abs(steering_angle)

        ######## Reward #1 - DIRECTION REWARD ########
        reward = direction_reward_fn(waypoints, closest_waypoints, heading)

        ######## Reward #2 - STEERING REWARD ########
        reward = steering_reward_fn(reward, steering)

        ######## Reward #3 - LANE REWARD ########
        reward = lane_reward_fn(reward, steering_angle, is_left)

        ######## Reward #4 - FAST LANE REWARD ########
        reward = fast_speed_reward_fn(reward, speed, steering, steps)

        ######## Reward #5 - SLOW TURN REWARD ########
        reward = slow_turn_reward_fn(reward, speed, steering, steps)

        ######## Reward #6 - OVERALL PROGRESS REWARD ########
        reward = progress_reward_fn(reward, progress, steps)

    return float(reward)
