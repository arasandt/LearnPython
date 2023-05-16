import math

# Lars Loop Track
MAX_WAYPOINT = 82
MAX_STEERING = 30
MIN_SPEED, MAX_SPEED = 1.0, 2.0
STEERING_SAVE_LENGTH = 10


class SaveSteering:
    def __init__(self):
        self.saved_steering_angles = [0] * STEERING_SAVE_LENGTH

    def add_element(self, value):
        self.saved_steering_angles.append(value)
        self.saved_steering_angles = self.saved_steering_angles[1:]

    def get_average(self):
        return sum(self.saved_steering_angles) / len(self.saved_steering_angles)


save_steering_obj = SaveSteering()


class Track:
    LOOKWAYAHEAD_WAYPOINT = 10

    @staticmethod
    def get_next_waypoint(next_point, ahead_waypoint):
        new_next_waypoint = next_point + ahead_waypoint
        if new_next_waypoint > MAX_WAYPOINT:
            new_next_waypoint = new_next_waypoint - MAX_WAYPOINT - 1
        return new_next_waypoint

    @staticmethod
    def get_direction_degree(waypoints, current_waypoint, next_waypoint):
        # Calculate the direction of the center line based
        next_point = waypoints[next_waypoint]
        prev_point = waypoints[current_waypoint]
        # Calculate the direction in radius, arctan2(dy, dx),
        track_direction = math.atan2(
            next_point[1] - prev_point[1], next_point[0] - prev_point[0]
        )
        # Convert to degree
        track_direction = math.degrees(track_direction)

        return track_direction

    def __init__(self, closest_waypoints, waypoints):
        self.lookwayahead_waypoint = self.LOOKWAYAHEAD_WAYPOINT
        self.closest_waypoints = closest_waypoints
        self.waypoints = waypoints

    def get_track_data(self):
        lookwayahead_angle = Track.get_direction_degree(
            self.waypoints,
            self.closest_waypoints[1],
            Track.get_next_waypoint(
                self.closest_waypoints[1], self.lookwayahead_waypoint
            ),
        )

        return lookwayahead_angle


class Reward:

    DIRECTION_LIMIT = 30
    SMOOTH_STEERING_THRESHOLD = 3

    def __init__(
        self,
        heading,
        speed,
        steering,
        steering_angle,
        progress,
        steps,
    ):
        self.heading = heading
        self.speed = speed
        self.steering = steering
        self.steering_angle = steering_angle
        self.progress = progress
        self.steps = steps

    @staticmethod
    def get_direction_diff(first_direction, second_direction):
        # Calculate the difference between the track direction and the heading direction of the car
        direction_diff = abs(first_direction - second_direction)

        if direction_diff > 180:
            direction_diff = 360 - direction_diff

        return direction_diff

    def calc_direction_reward(self, lookwayahead_angle):
        self.lookwayahead_direction_diff = Reward.get_direction_diff(
            lookwayahead_angle, self.heading
        )

        self.direction_reward = Reward.DIRECTION_LIMIT / (
            Reward.DIRECTION_LIMIT + self.lookwayahead_direction_diff
        )

        self.direction_reward *= 3

    def calc_steering_reward(self):
        self.steering_reward = MAX_STEERING / (MAX_STEERING + self.steering)

    def calc_speed_reward(self):
        self.speed_reward = self.speed / MAX_SPEED

    def calc_progress_reward(self):
        self.progress_reward = 0.1

        if self.steps > 5:
            self.progress_reward = self.progress / self.steps

    def calc_consistent_steering_reward(self):
        average_steering = save_steering_obj.get_average()
        steering_threshold_higher = average_steering + self.SMOOTH_STEERING_THRESHOLD
        steering_threshold_lower = average_steering - self.SMOOTH_STEERING_THRESHOLD

        if steering_threshold_lower <= self.steering_angle <= steering_threshold_higher:
            self.consistent_steering_reward = 0.5
        else:
            higher_reward = 0.25 / (self.steering_angle - steering_threshold_higher)
            lower_reward = 0.25 / (self.steering_angle - steering_threshold_lower)
            self.consistent_steering_reward = max(higher_reward, lower_reward)

        save_steering_obj.add_element(self.steering_angle)

    def get_all_rewards(self, display=False):
        if display:
            print(f"direction_reward: {self.direction_reward}")
            print(f"steering_reward: {self.steering_reward}")
            print(f"speed_reward: {self.speed_reward}")
            print(f"consistent_steering_reward: {self.consistent_steering_reward}")
            print(f"progress_reward: {self.progress_reward}")
        total_rewards = (
            self.direction_reward
            + self.steering_reward
            + self.speed_reward
            + self.consistent_steering_reward
        ) * self.progress_reward

        return total_rewards


def reward_function(params):

    steering_angle = params["steering_angle"]
    steering = abs(steering_angle)
    speed = params["speed"]

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        rewards = 0
    ######## Check #2 - OUTLIERS CHECK ########
    # change this accordingly for MAX SPEED. This number is good for MAX SPEED = 3.0
    # elif (speed >= MAX_SPEED * 0.75 and steering >= MAX_STEERING / 4) or (
    #     speed <= MIN_SPEED * 1.25 and steering <= MAX_STEERING / 3
    # ):
    #     rewards = 0
    else:
        # Read input variables
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        heading = params["heading"]
        steps = params["steps"]
        progress = params["progress"]

        track = Track(closest_waypoints, waypoints)
        lookwayahead_angle = track.get_track_data()

        reward = Reward(
            heading,
            speed,
            steering,
            steering_angle,
            progress,
            steps,
        )

        reward.calc_direction_reward(lookwayahead_angle)
        reward.calc_steering_reward()
        reward.calc_speed_reward()
        reward.calc_progress_reward()
        reward.calc_consistent_steering_reward()

        rewards = reward.get_all_rewards()

    return float(rewards)
