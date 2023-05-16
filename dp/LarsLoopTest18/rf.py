# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.88
# Loss type	Mean squared error
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	18
# Number of epochs	4
# Speed: [ 1.3 : 2.2 ] m/s
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
MIN_SPEED, MAX_SPEED = 1.3, 2.2


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


def speed_reward_fn(
    reward,
    speed,
    direction_diff,
    steering,
    all_wheels_on_track,
    is_left,
    closest_waypoints,
):

    speed_reward = speed / (MAX_SPEED + speed)
    uturn_lane_1 = list(range(18, 20 + 1))
    slight_lane_1 = list(range(25, 27 + 1))
    slight_lane_2 = list(range(36, 37 + 1))
    uturn_lane_4 = list(range(63, 64 + 1))
    slight_lane_3 = list(range(71, 72 + 1))
    slight_lane_4 = list(range(44, 45 + 1))

    if closest_waypoints[1] in uturn_lane_1:
        if speed <= max(MAX_SPEED * 0.45, MIN_SPEED):
            pass
        else:
            speed_reward = MAX_SPEED / (speed + MAX_SPEED)
    elif closest_waypoints[1] in slight_lane_1 + slight_lane_3 + slight_lane_4:
        if speed <= max(MAX_SPEED * 0.7, MIN_SPEED):
            pass
        else:
            speed_reward = MAX_SPEED / (speed + MAX_SPEED)
    elif closest_waypoints[1] in slight_lane_2:
        if speed <= max(MAX_SPEED * 0.8, MIN_SPEED):
            pass
        else:
            speed_reward = MAX_SPEED / (speed + MAX_SPEED)
    elif closest_waypoints[1] in uturn_lane_4:
        if speed <= max(MAX_SPEED * 0.55, MIN_SPEED):
            pass
        else:
            speed_reward = MAX_SPEED / (speed + MAX_SPEED)

    if steering < STEERING_THRESHOLD and direction_diff < STEERING_THRESHOLD:
        if steering > 0.5:
            speed_reward += 0.25
        else:
            speed_reward += 0.5

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
    closest_waypoints,
):
    edge_reward = 0.01
    border_factor = 0.5
    border_reward = 0

    distance_from_border = 0.5 * track_width - distance_from_center
    border_reward = (
        border_factor
        * distance_from_border
        / (distance_from_center + distance_from_border)
    )

    # right lane
    # right_lane_1 = list(range(77, 80 + 1))
    # mid_lane_1 = list(range(0, 3 + 1))
    left_lane_1 = list(range(4, 7 + 1))
    # mid_lane_2 = list(range(8, 10 + 1))
    right_lane_2 = list(range(11, 17 + 1))
    # mid_lane_3 = list(range(18, 19 + 1))
    left_lane_2 = list(range(20, 24 + 1))
    # mid_lane_4 = list(range(26, 26 + 1))
    right_lane_3 = list(range(28, 29 + 1))
    left_lane_3 = list(range(32, 34 + 1))
    right_lane_4 = list(range(39, 42 + 1))
    left_lane_5 = list(range(45, 46 + 1))
    right_lane_5 = list(range(49, 58 + 1))
    left_lane_6 = list(range(67, 70 + 1))

    # if closest_waypoints[1] in right_lane_1:
    #     if not is_left:
    #         edge_reward = 1
    # elif closest_waypoints[1] in mid_lane_1 + mid_lane_2 + mid_lane_3:
    #     edge_reward -= distance_from_center
    if closest_waypoints[1] in left_lane_2 + left_lane_3 + left_lane_5 + left_lane_6:
        if is_left:
            edge_reward = 1 + border_reward
    elif closest_waypoints[1] in left_lane_1:
        if is_left:
            edge_reward = 1 + border_reward
        else:
            edge_reward = -1
    elif (
        closest_waypoints[1]
        in right_lane_2 + right_lane_3 + right_lane_4 + right_lane_5
    ):
        if not is_left:
            edge_reward = 1 + border_reward
    # right turn
    elif steering_angle <= (-20 + STEERING_THRESHOLD * 1.5):
        edge_reward = 1
        if is_left:
            edge_reward *= 0.5
        if not all_wheels_on_track:
            edge_reward += 0.02
    # left turn
    elif steering_angle >= MAX_STEERING - (STEERING_THRESHOLD * 1.5):
        edge_reward = 1
        if not is_left:
            edge_reward *= 0.5
        if all_wheels_on_track:
            edge_reward += 0.04

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
        reward = 0.01
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

        direction_diff = get_direction_diff(immediate_direction, lookahead_direction)

        ######## Reward #1 - DIRECTION REWARD ########
        reward, turn_direction = direction_reward_fn(
            immediate_direction, lookahead_direction, heading, steering_angle
        )
        ######## Reward #2 - SPEED REWARD ########
        reward = speed_reward_fn(
            reward,
            speed,
            direction_diff,
            steering,
            all_wheels_on_track,
            is_left,
            closest_waypoints,
        )

        ######## Reward #3 - PROGRESS REWARD ########
        reward = progress_reward_fn(reward, progress, steps)

        ######## Reward #4 - USE BEST PATH REWARD ########
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
        )

    return float(reward)
