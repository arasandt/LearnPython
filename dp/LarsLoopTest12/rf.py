# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.88
# Loss type	Mean squared error
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	18
# Number of epochs	4
# Speed: [ 1.0 : 2.2 ] m/s
# Steering angle: [ -20 : 30 ] °
# Training time 4 hours until stoppage

# The car relies on reward varying between behaviours to find gradients that can lead to improvement.
# If that is missing, the model will struggle to improve.

import math

# Lars Loop Track
STEERING_THRESHOLD = 3
LOOKAHEAD_WAYPOINT = 4
MAX_WAYPOINT = 82
MAX_STEERING = 30
MIN_SPEED, MAX_SPEED = 1.0, 2.2


def get_next_waypoint(next_point, ahead_waypoint):
    new_next_waypoint = next_point + ahead_waypoint
    if new_next_waypoint > MAX_WAYPOINT:
        new_next_waypoint = new_next_waypoint - MAX_WAYPOINT - 1
    return new_next_waypoint


def get_immediate_direction(waypoints, closest_waypoints):
    # Calculate the direction of the center line based
    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]
    # Calculate the direction in radius, arctan2(dy, dx),
    track_direction = math.atan2(
        next_point[1] - prev_point[1], next_point[0] - prev_point[0]
    )
    # Convert to degree
    track_direction = math.degrees(track_direction)

    return track_direction


def get_lookahead_direction(waypoints, closest_waypoints):
    # Calculate the direction of the center line based
    next_point = waypoints[get_next_waypoint(closest_waypoints[1], LOOKAHEAD_WAYPOINT)]
    prev_point = waypoints[closest_waypoints[0]]
    # Calculate the direction in radius, arctan2(dy, dx),
    track_direction = math.atan2(
        next_point[1] - prev_point[1], next_point[0] - prev_point[0]
    )
    # Convert to degree
    track_direction = math.degrees(track_direction)

    return track_direction


def get_direction_diff(first_direction, second_direction):
    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(first_direction - second_direction)

    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    return direction_diff


def get_turn_direction(immediate_direction, lookahead_direction, heading):
    if immediate_direction < 0:
        immediate_direction += 360
    if lookahead_direction < 0:
        lookahead_direction += 360
    if heading < 0:
        heading += 360

    # sweep window is 90 degree
    difference = abs(immediate_direction - lookahead_direction)
    difference_360 = 360 - difference

    if difference <= MAX_STEERING * 3:
        if lookahead_direction > immediate_direction:
            direction = "left"
        else:
            direction = "right"
    elif difference_360 <= MAX_STEERING * 3:
        if lookahead_direction > immediate_direction:
            direction = "right"
        else:
            direction = "left"
    else:
        direction = 0
    return direction, immediate_direction, lookahead_direction, heading


def direction_reward_fn(
    immediate_direction, lookahead_direction, heading, steering_angle
):
    direction_reward = 1
    direction_diff = get_direction_diff(immediate_direction, lookahead_direction)

    (
        turn_direction,
        new_immediate_direction,
        new_lookahead_direction,
        new_heading,
    ) = get_turn_direction(immediate_direction, lookahead_direction, heading)
    if not turn_direction:
        return direction_reward * 0.1, ""

    if new_immediate_direction <= new_heading <= new_lookahead_direction:
        pass
    elif new_immediate_direction >= new_heading >= new_lookahead_direction:
        pass
    elif immediate_direction >= heading >= lookahead_direction:
        pass
    elif immediate_direction <= heading <= lookahead_direction:
        pass
    else:
        direction_reward *= 0.75

    # steering angle is within the direction difference angle, else existing reward
    if turn_direction == "left":
        if direction_diff >= steering_angle >= -0.1:
            direction_reward += 0.5
        else:
            direction_reward -= 0.25
    elif turn_direction == "right":
        if -direction_diff <= steering_angle <= 0.1:
            direction_reward += 0.5
        else:
            direction_reward -= 0.25

    return direction_reward, turn_direction


def speed_reward_fn(reward, speed, direction_diff):

    # Initialize speed reward based on speed.
    speed_reward = speed / MAX_SPEED

    if direction_diff > STEERING_THRESHOLD * 1.5:
        direction_diff_check = min(MAX_STEERING, direction_diff)
        # cut down the speed reward based on how much direction diff it is
        speed_reward = speed_reward * (
            MAX_STEERING / (direction_diff_check + MAX_STEERING)
        )

    return reward + speed_reward


def progress_reward_fn(reward, progress, steps):
    progress_reward = 0.001

    if steps > 5:
        progress_reward = progress / steps

    return reward + progress_reward * 2


def edge_reward_fn(
    reward,
    is_left,
    all_wheels_on_track,
    steering_angle,
    direction_diff,
    track_width,
    distance_from_center,
    turn_direction,
):
    edge_reward = 1
    incorrect_lane_factor = 0.5
    border_factor = 0.5
    border_reward = 0

    distance_from_border = 0.5 * track_width - distance_from_center
    border_reward = (
        border_factor
        * distance_from_border
        / (distance_from_center + distance_from_border)
    )

    if not is_left:
        if (
            turn_direction == "right"
            and direction_diff >= 10
            and not all_wheels_on_track
        ):
            edge_reward += 0.2
            edge_reward += border_reward
        elif turn_direction == "left" and direction_diff > STEERING_THRESHOLD * 2.5:
            edge_reward = edge_reward - incorrect_lane_factor - border_reward
            # edge_reward *= 1.5
        else:
            edge_reward += border_reward

    else:
        edge_reward -= incorrect_lane_factor
        edge_reward += border_reward

    return reward + edge_reward


def reward_function(params):

    steering_angle = params["steering_angle"]
    # steering = abs(steering_angle)
    speed = params["speed"]

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        reward = 0
    else:
        # Read input variables
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        heading = params["heading"]
        steps = params["steps"]
        progress = params["progress"]
        is_left = params["is_left_of_center"]
        all_wheels_on_track = params["all_wheels_on_track"]
        track_width = params["track_width"]
        distance_from_center = params["distance_from_center"]

        immediate_direction = get_immediate_direction(waypoints, closest_waypoints)
        lookahead_direction = get_lookahead_direction(waypoints, closest_waypoints)

        ######## Reward #1 - DIRECTION REWARD ########
        reward, turn_direction = direction_reward_fn(
            immediate_direction, lookahead_direction, heading, steering_angle
        )

        ######## Reward #2 - SPEED REWARD ########
        direction_diff = get_direction_diff(immediate_direction, lookahead_direction)
        reward = speed_reward_fn(reward, speed, direction_diff)

        ######## Reward #3 - PROGRESS REWARD ########
        # reward = progress_reward_fn(reward, progress, steps)

        ######## Reward #4 - USE INNER LOOP REWARD ########
        reward = edge_reward_fn(
            reward,
            is_left,
            all_wheels_on_track,
            steering_angle,
            direction_diff,
            track_width,
            distance_from_center,
            turn_direction,
        )

    return float(reward)
