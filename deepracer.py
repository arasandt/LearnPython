import math


def reward_function(params):

    # Read input variables
    waypoints = params["waypoints"]
    closest_waypoints = params["closest_waypoints"]
    heading = params["heading"]
    steps = params["steps"]
    speed = params["speed"]
    progress = params["progress"]
    steering = abs(params["steering_angle"])

    # Initialize the reward with typical value
    reward = 0
    direction_reward = 1.0
    progress_reward = 0
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
    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff
    # Penalize the reward if the difference is too large
    if direction_diff > DIRECTION_THRESHOLD:
        direction_reward *= 0.5

    ######## Reward #2 - STEERING REWARD ########
    if steering > ABS_STEERING_THRESHOLD:
        direction_reward *= 0.7

    ######## Reward #3 - PROGRESS REWARD ########
    if steps > 5:
        progress_reward = progress * 1.33 / steps

    reward = direction_reward + progress_reward

    ######## Reward #4 - FAST LANE REWARD ########
    if steps > 5:
        if steering < 0.5 and speed > 2:
            reward *= (speed / 2) * 1.6
        elif steering < 1 and speed > 1.4:
            reward *= (speed / 1.4) * 1.2

    if params["is_offtrack"]:
        reward = 0

    return float(reward)
