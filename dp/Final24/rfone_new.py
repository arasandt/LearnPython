# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.88
# Loss type	Mean squared error
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	18
# Number of epochs	4
# Speed: [ 1.2 : 2.4 ] m/s
# Steering angle: [ -22.5 : 30 ] °
# Training time 4 + 2 hours

import math

# Lars Loop Track
DIRECTION_THRESHOLD = 15
ABS_STEERING_THRESHOLD = 22.5
MIN_SPEED, MAX_SPEED = 1.2, 2.4
# Lars Loop Track


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


def steering_reward_fn(reward, steering):
    steering_reward = 1

    if steering > ABS_STEERING_THRESHOLD:
        steering_reward = 0.8

    return reward + steering_reward


def lane_reward_fn(reward, steering_angle, is_left):
    lane_reward = 0
    steering_threshhold_1 = 2

    if (steering_angle <= -ABS_STEERING_THRESHOLD and not is_left) or (
        steering_angle >= ABS_STEERING_THRESHOLD and is_left
    ):
        lane_reward = 0.66

    if abs(steering_angle) <= steering_threshhold_1 and not is_left:
        lane_reward = 0.33

    return reward + lane_reward


def fast_speed_reward_fn(reward, speed, steering):
    speed_threshold_1 = MAX_SPEED * 0.75
    speed_reward = 0

    if speed_threshold_1 <= speed <= MAX_SPEED:
        speed_reward = speed / MAX_SPEED

    return reward + speed_reward


def progress_reward_fn(reward, progress, steps):
    progress_reward = 0

    if steps > 5:
        progress_reward = progress / steps

    return reward * progress_reward


def straight_reward_fn(reward, steering):
    steering_reward = 0
    steering_threshhold_1 = 2

    if steering <= steering_threshhold_1:
        steering_reward = steering_threshhold_1 + 0.1 - steering

    return reward + steering_reward


def slow_turn_reward_fn(reward, speed, steering):
    speed_threshold = MIN_SPEED * 1.25
    steering_threshhold = ABS_STEERING_THRESHOLD + 2.5
    slow_reward = 0

    if speed <= speed_threshold and steering >= steering_threshhold:
        slow_reward = (
            (speed_threshold / speed) + MAX_SPEED + (speed_threshold - MIN_SPEED)
        )

    return reward + slow_reward


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

        ######## Reward #4 - FAST SPEED REWARD ########
        reward = fast_speed_reward_fn(reward, speed, steering)

        ######## Reward #5 - STRAIGHT REWARD ########
        reward = straight_reward_fn(reward, steering)

        ######## Reward #6 - SLOW TURN REWARD ########
        reward = slow_turn_reward_fn(reward, speed, steering)

        ######## Reward #5 - PROGRESS REWARD ########
        reward = progress_reward_fn(reward, progress, steps)

    return float(reward)
