# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.88
# Loss type	Mean squared error
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	18
# Number of epochs	4
# Speed: [ 1.2 : 3.0 ] m/s
# Steering angle: [ -20 : 30 ] °
# Training time 4 hours until stoppage

# The car relies on reward varying between behaviours to find gradients that can lead to improvement.
# If that is missing, the model will struggle to improve.

import math

# Lars Loop Track
STEERING_THRESHOLD = 3
LOOKAHEAD_WAYPOINT = 4
LOOKWAYAHEAD_WAYPOINT = 9
MAX_WAYPOINT = 82
MAX_STEERING = 30
MIN_SPEED, MAX_SPEED = 1.2, 3.0


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


def get_lookwayahead_direction(waypoints, closest_waypoints):
    # Calculate the direction of the center line based
    next_point = waypoints[
        get_next_waypoint(closest_waypoints[1], LOOKWAYAHEAD_WAYPOINT)
    ]
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
    angle = min(direction_diff, 15)
    if abs(steering_angle) <= angle:
        direction_reward += 0.5

    # if turn_direction == "left":
    #     if direction_diff >= c >= -0.1:
    #         direction_reward += 0.5
    #     else:
    #         direction_reward -= 0.25
    # elif turn_direction == "right":
    #     if -direction_diff <= steering_angle <= 0.1:
    #         direction_reward += 0.5
    #     else:
    #         direction_reward -= 0.25

    return direction_reward, turn_direction


def speed_reward_fn(reward, speed, direction_diff, steering, all_wheels_on_track):

    # Initialize speed reward based on speed.
    speed_reward = 2 * speed / MAX_SPEED

    if direction_diff >= MAX_STEERING - STEERING_THRESHOLD * 3:
        speed_reward = direction_diff / (direction_diff + MAX_STEERING)
    elif direction_diff > STEERING_THRESHOLD * 3:
        # cut down the speed reward based on how much direction diff it is
        speed_reward = MAX_STEERING / (direction_diff + MAX_STEERING)

    if steering < 1:
        speed_reward *= 1.5

    if speed > speed * 0.9 and not all_wheels_on_track:
        speed_reward *= 0.95

    return reward + speed_reward


def progress_reward_fn(reward, progress, steps):
    progress_reward = 0.001

    if steps > 5:
        progress_reward = progress / steps

    return reward + progress_reward * 3


def straightahead_reward_fn(
    reward,
    immediate_direction,
    lookahead_direction,
    lookwayahead_direction,
    speed,
    steering,
    heading,
    all_wheels_on_track,
):
    straight_reward = 0.001

    near_direction_diff = get_direction_diff(heading, lookahead_direction)
    far_direction_diff = get_direction_diff(heading, lookwayahead_direction)

    if far_direction_diff <= STEERING_THRESHOLD:
        straight_reward = 2 * speed / MAX_SPEED
    elif near_direction_diff <= STEERING_THRESHOLD:
        straight_reward = speed / MAX_SPEED

    return reward + straight_reward


def edge_reward_fn(
    reward,
    is_left,
    all_wheels_on_track,
    steering_angle,
    direction_diff,
    track_width,
    distance_from_center,
    turn_direction,
    closest_waypoints,
    speed,
):
    edge_reward = 0
    border_factor = 1

    distance_from_border = 0.5 * track_width - distance_from_center
    border_reward = (
        border_factor
        * distance_from_border
        / (distance_from_center + distance_from_border)
    )

    if not is_left:
        if (
            abs(steering_angle) <= STEERING_THRESHOLD
            and speed > (MAX_SPEED * 0.9)
            and closest_waypoints[1] in [14, 15, 16, 17]
        ):
            edge_reward = 1
        elif (
            turn_direction == "right"
            and direction_diff >= STEERING_THRESHOLD * 3
            and direction_diff <= 20
            and not all_wheels_on_track
        ):
            edge_reward += 0.5
        elif (
            turn_direction == "right"
            and direction_diff >= STEERING_THRESHOLD * 3
            and direction_diff <= 20
        ):
            edge_reward += border_reward

    return reward + edge_reward


def reward_function(params):

    steering_angle = params["steering_angle"]
    steering = abs(steering_angle)
    speed = params["speed"]

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        reward = 0
    ######## Check #2 - OUTLIERS CHECK ########
    elif (speed >= MAX_SPEED * 0.75 and steering >= MAX_STEERING // 4) or (
        speed <= (MAX_SPEED - MIN_SPEED) * 1.5 and steering <= STEERING_THRESHOLD
    ):
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
        lookwayahead_direction = get_lookwayahead_direction(
            waypoints, closest_waypoints
        )

        ######## Reward #1 - DIRECTION REWARD ########
        reward, turn_direction = direction_reward_fn(
            immediate_direction, lookahead_direction, heading, steering_angle
        )

        ######## Reward #2 - SPEED REWARD ########
        direction_diff = get_direction_diff(immediate_direction, lookahead_direction)
        reward = speed_reward_fn(
            reward, speed, direction_diff, steering, all_wheels_on_track
        )

        ######## Reward #3 - PROGRESS REWARD ########
        reward = progress_reward_fn(reward, progress, steps)

        ######## Reward #4 - PROGRESS REWARD ########
        reward = straightahead_reward_fn(
            reward,
            immediate_direction,
            lookahead_direction,
            lookwayahead_direction,
            speed,
            steering,
            heading,
            all_wheels_on_track,
        )

        ######## Reward #5 - USE INNER LOOP REWARD ########
        reward = edge_reward_fn(
            reward,
            is_left,
            all_wheels_on_track,
            steering_angle,
            direction_diff,
            track_width,
            distance_from_center,
            turn_direction,
            closest_waypoints,
            speed,
        )

    return float(reward)
