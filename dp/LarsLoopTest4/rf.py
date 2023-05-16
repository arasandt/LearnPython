# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.88
# Loss type	Mean squared error
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	18
# Number of epochs	4
# Speed: [ 1.3 : 2.6 ] m/s
# Steering angle: [ -20 : 30 ] °
# Training time 4 + 2 hours

import math

# Lars Loop Track
STEERING_THRESHOLD = 3
LOOKAHEAD_WAYPOINT = 4
MAX_WAYPOINT = 82
MAX_STEERING = 30
MIN_SPEED, MAX_SPEED = 1.3, 2.6


def get_next_waypoint(next_point):
    new_next_waypoint = next_point + LOOKAHEAD_WAYPOINT
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
    next_point = waypoints[get_next_waypoint(closest_waypoints[1])]
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
    if abs(immediate_direction - lookahead_direction) <= MAX_STEERING * 3:
        if lookahead_direction > immediate_direction:
            direction = "left"
        else:
            direction = "right"
    elif 360 - abs(immediate_direction - lookahead_direction) <= MAX_STEERING * 3:
        if lookahead_direction > immediate_direction:
            direction = "right"
        else:
            direction = "left"
    else:
        direction = 0
    return direction, immediate_direction, lookahead_direction, heading


def direction_reward_fn(immediate_direction, lookahead_direction, heading):
    direction_reward = 1

    (
        turn_direction,
        new_immediate_direction,
        new_lookahead_direction,
        new_heading,
    ) = get_turn_direction(immediate_direction, lookahead_direction, heading)
    if not turn_direction:
        return 0, 0

    if (
        new_immediate_direction <= new_heading <= new_lookahead_direction
    ) and turn_direction == "left":
        pass
    elif (
        new_immediate_direction >= new_heading >= new_lookahead_direction
    ) and turn_direction == "right":
        pass
    elif (
        immediate_direction >= heading >= lookahead_direction
    ) and turn_direction == "right":
        pass
    elif (
        immediate_direction <= heading <= lookahead_direction
    ) and turn_direction == "left":
        pass
    else:
        direction_reward = 0.15

    return direction_reward, turn_direction


def speed_reward_fn(reward, speed, direction_diff):

    min_speed_threshold = MIN_SPEED * 1.15
    max_speed_threshold = MAX_SPEED * 0.925

    threshold_diff = max_speed_threshold - min_speed_threshold

    # Make default speed less so that it does not interfere with other two defined rewards below
    speed_reward = 0.5 * speed / (speed + threshold_diff)

    if direction_diff <= STEERING_THRESHOLD and speed >= max_speed_threshold:
        speed_reward = speed / MAX_SPEED
    elif (
        direction_diff >= MAX_STEERING - (STEERING_THRESHOLD * 2)
        and speed <= min_speed_threshold
    ):
        speed_reward = MIN_SPEED / speed

    return reward + speed_reward


def progress_reward_fn(reward, progress, steps):
    progress_reward = 0

    if steps > 5:
        progress_reward = progress / steps

    return reward + progress_reward


def edge_reward_fn(reward, is_left, all_wheels_on_track, steering_angle):
    edge_reward = 0

    # steering_angle <= -(MAX_STEERING - (STEERING_THRESHOLD * 2)) and not is_left
    if (steering_angle <= (-20 + STEERING_THRESHOLD * 1.5) and not is_left) or (
        steering_angle >= MAX_STEERING - (STEERING_THRESHOLD * 1.5) and is_left
    ):
        edge_reward = 0.14
        if not all_wheels_on_track:
            edge_reward += 0.07

    return reward + edge_reward


def reward_function(params):

    steering_angle = params["steering_angle"]
    steering = abs(steering_angle)
    speed = params["speed"]

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        reward = 0
    ######## Check #2 - OUTLIERS CHECK ########
    elif (
        speed >= MAX_SPEED - 0.2 and steering >= MAX_STEERING - STEERING_THRESHOLD * 2
    ) or (speed <= MIN_SPEED + 0.4 and steering <= STEERING_THRESHOLD):
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

        immediate_direction = get_immediate_direction(waypoints, closest_waypoints)
        lookahead_direction = get_lookahead_direction(waypoints, closest_waypoints)

        ######## Reward #1 - DIRECTION REWARD ########
        reward, turn_direction = direction_reward_fn(
            immediate_direction, lookahead_direction, heading
        )

        if not turn_direction:  # not within the sweeping window
            return reward

        ######## Check #3 - STEERING CHECK ########
        direction_diff = get_direction_diff(immediate_direction, lookahead_direction)

        # steering angle is within the direction difference angle, else existing reward
        if (
            turn_direction == "left"
            and direction_diff >= steering_angle >= -STEERING_THRESHOLD
        ):
            pass
        elif (
            turn_direction == "right"
            and -direction_diff <= steering_angle <= STEERING_THRESHOLD
        ):
            pass
        else:
            return reward

        ######## Reward #2 - SPEED REWARD ########
        reward = speed_reward_fn(reward, speed, direction_diff)

        ######## Reward #3 - PROGRESS REWARD ########
        reward = progress_reward_fn(reward, progress, steps)

        ######## Reward #4 - USE INNER LOOP REWARD ########
        reward = edge_reward_fn(reward, is_left, all_wheels_on_track, steering_angle)

    return float(reward)
