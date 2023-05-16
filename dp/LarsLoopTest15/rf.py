# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.88
# Loss type	Mean squared error
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	18
# Number of epochs	4
# Speed: [ 1.0 : 2.0] m/s
# Steering angle: [ -22.5 : 30 ] °
# Training time 4 hours until stoppage

# The car relies on reward varying between behaviours to find gradients that can lead to improvement.
# If that is missing, the model will struggle to improve.

import math

# Lars Loop Track
DIRECTION_THRESHOLD = 5
MAX_STEERING = 30
MAX_SPEED = 2


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
        direction_reward *= 0.75

    return direction_reward


def progress_reward_fn(reward, progress, steps):
    progress_reward = 0.001

    if steps > 5:
        progress_reward = progress / steps

    return reward + progress_reward * 2


def right_lane_fast_1_fn(speed, is_left, steering):
    reward = speed / MAX_SPEED
    steering_threshhold = 1.5

    if is_left:
        reward = 0.01
    if steering < steering_threshhold:
        reward += steering_threshhold / (steering + steering_threshhold)

    return reward


def straight_lane_fast_1_fn(speed, steering, progress, steps):
    reward = speed / MAX_SPEED
    steering_threshhold = 7.5

    if steering < steering_threshhold:
        reward += steering_threshhold / (steering + steering_threshhold)

    return progress_reward_fn(reward, progress, steps)


def left_lane_fast_2_fn(speed, is_left, steering):
    if speed <= 0.85 * MAX_SPEED:
        reward = speed / MAX_SPEED
    else:
        reward = speed / MAX_SPEED * math.pow(0.85, 2)

    if not is_left:
        reward = 0.01
    if steering < 3:
        reward += steering / MAX_STEERING

    return reward


def slow_lane_2_fn(speed, is_left, steering):
    if speed <= 0.5 * MAX_SPEED:
        reward = speed / MAX_SPEED
    else:
        reward = speed / MAX_SPEED * math.pow(0.5, 2)

    if is_left:
        reward = 0.01
    if steering > 15:
        reward += steering / MAX_STEERING

    return reward


def left_lane_fast_1_fn(speed, is_left, steering):
    reward = speed / MAX_SPEED

    if not is_left:
        reward = 0.01
    if steering < 1:
        reward += steering / MAX_STEERING

    return reward


def left_lane_fast_4_fn(speed, is_left, steering):
    if speed <= 0.5 * MAX_SPEED:
        reward = speed / MAX_SPEED
    else:
        reward = speed / MAX_SPEED * math.pow(0.5, 2)

    if steering <= 15:
        reward += steering / MAX_STEERING

    return reward


def slow_lane_1_fn(speed, is_left, steering, distance_from_center):
    if speed <= 0.3 * MAX_SPEED:
        reward = speed / MAX_SPEED
    else:
        reward = speed / MAX_SPEED * math.pow(0.3, 2)

    reward -= distance_from_center * 0.1

    if steering > 20:
        reward += steering / MAX_STEERING

    return reward


def reward_function(params):

    steering_angle = params["steering_angle"]
    steering = abs(steering_angle)
    speed = params["speed"]

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        return 0.0
    else:
        # Read input variables
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        heading = params["heading"]
        steps = params["steps"]
        progress = params["progress"]
        is_left = params["is_left_of_center"]
        # all_wheels_on_track = params["all_wheels_on_track"]
        # track_width = params["track_width"]
        distance_from_center = params["distance_from_center"]

        right_lane_fast_1 = list(range(49, 61 + 1))  #
        right_lane_fast_2 = list(range(74, 80 + 1))
        right_lane_fast_3 = list(range(0, 2 + 1))  #
        right_lane_fast_4 = list(range(8, 18 + 1))  #

        straight_lane_fast_1 = list(range(28, 46 + 1))  #

        left_lane_fast_1 = list(range(66, 72 + 1))  #
        left_lane_fast_2 = list(range(3, 7 + 1))  #
        left_lane_fast_3 = list(range(22, 27 + 1))  #
        left_lane_fast_4 = list(range(47, 48 + 1))  #

        slow_lane_1 = list(range(62, 65 + 1))  #
        slow_lane_2 = list(range(73, 73 + 1))  #
        slow_lane_3 = list(range(19, 21 + 1))  #

        initial_reward = direction_reward_fn(waypoints, closest_waypoints, heading)
        if (
            closest_waypoints[1]
            in right_lane_fast_1
            + right_lane_fast_2
            + right_lane_fast_3
            + right_lane_fast_4
        ):
            return initial_reward + right_lane_fast_1_fn(speed, is_left, steering)
        elif closest_waypoints[1] in straight_lane_fast_1:
            return initial_reward + straight_lane_fast_1_fn(
                speed, steering, progress, steps
            )

        elif closest_waypoints[1] in left_lane_fast_1 + left_lane_fast_3:

            return initial_reward + left_lane_fast_1_fn(speed, is_left, steering)
        elif closest_waypoints[1] in left_lane_fast_4:
            return initial_reward + left_lane_fast_4_fn(speed, is_left, steering)
        elif closest_waypoints[1] in left_lane_fast_2:
            return initial_reward + left_lane_fast_2_fn(speed, is_left, steering)
        elif closest_waypoints[1] in slow_lane_1 + slow_lane_3:
            return initial_reward + slow_lane_1_fn(
                speed, is_left, steering, distance_from_center
            )
        elif closest_waypoints[1] in slow_lane_2:
            return initial_reward + slow_lane_2_fn(speed, is_left, steering)

    return 0.01
