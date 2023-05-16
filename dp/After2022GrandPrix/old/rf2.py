# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.87
# Loss type	Huber
# "loss_type": "mean squared error",
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	100
# Number of epochs	3
# Speed: [ 1.2 : 2.0 ] m/s
# Steering angle: [ -20 : 30 ] °
# Training time 12 hours

# Train after knowing the path of the track. Either make sure the direction (left or right) is taken care or
# using the RF after knowing the path.
# BUT LOOKS LIKE AFTER 25 EPISODES IT STARTED TO WORK

import math

MAX_STEERING = 30
MIN_SPEED, MAX_SPEED = 1.2, 2.0


class Track:
    LOOKWAYAHEAD_WAYPOINT = 10

    def get_next_waypoint(self, next_point, ahead_waypoint):
        new_next_waypoint = next_point + ahead_waypoint
        if new_next_waypoint > self.MAX_WAYPOINT:
            new_next_waypoint = new_next_waypoint - self.MAX_WAYPOINT - 1
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

    def __init__(self, closest_waypoints, waypoints, heading):
        self.lookwayahead_waypoint = self.LOOKWAYAHEAD_WAYPOINT
        self.lookahead_waypoint = self.lookwayahead_waypoint // 2
        self.closest_waypoints = closest_waypoints
        self.waypoints = waypoints
        self.MAX_WAYPOINT = len(self.waypoints) - 1
        self.heading = heading

    @staticmethod
    def get_turn_direction(immediate_direction, lookahead_direction):
        window = 90

        if immediate_direction < 0:
            immediate_direction += 360
        if lookahead_direction < 0:
            lookahead_direction += 360

        # sweep window is 90 degree
        difference = abs(immediate_direction - lookahead_direction)
        difference_360 = 360 - difference

        if difference <= window:
            if lookahead_direction > immediate_direction:
                direction = "left"
            else:
                direction = "right"
        elif difference_360 <= window:
            if lookahead_direction > immediate_direction:
                direction = "right"
            else:
                direction = "left"
        else:
            direction = 0
        return direction

    def get_track_data(self):
        lookwayahead_angle = Track.get_direction_degree(
            self.waypoints,
            self.closest_waypoints[1],
            self.get_next_waypoint(
                self.closest_waypoints[1], self.lookwayahead_waypoint
            ),
        )

        lookahead_angle = Track.get_direction_degree(
            self.waypoints,
            self.closest_waypoints[1],
            self.get_next_waypoint(self.closest_waypoints[1], self.lookahead_waypoint),
        )

        immediate_angle = Track.get_direction_degree(
            self.waypoints,
            self.closest_waypoints[0],
            self.closest_waypoints[1],
        )

        turn_direction = Track.get_turn_direction(immediate_angle, lookahead_angle)

        return lookwayahead_angle, lookahead_angle, immediate_angle, turn_direction


class Reward:

    DIRECTION_LIMIT = 30
    SLOWDOWN_DIRECTION_LIMIT = 10
    FASTLANE_DIRECTION_LIMIT = 6

    def __init__(
        self,
        heading,
        speed,
        steering,
        steering_angle,
        is_left,
        distance_from_center,
        track_width,
        progress,
        steps,
        turn_direction,
    ):
        self.heading = heading
        self.speed = speed
        self.steering = steering
        self.steering_angle = steering_angle
        self.is_left = is_left
        self.progress = progress
        self.steps = steps
        self.turn_direction = turn_direction

        distance_from_border = 0.5 * track_width - distance_from_center
        self.border_reward = distance_from_border / (
            distance_from_center + distance_from_border
        )

    @staticmethod
    def get_direction_diff(first_direction, second_direction):
        # Calculate the difference between the track direction and the heading direction of the car
        direction_diff = abs(first_direction - second_direction)

        if direction_diff > 180:
            direction_diff = 360 - direction_diff

        return direction_diff

    def calc_direction_reward(self, lookahead_angle):
        self.lookahead_direction_diff = Reward.get_direction_diff(
            lookahead_angle, self.heading
        )

        self.direction_reward = Reward.DIRECTION_LIMIT / (
            Reward.DIRECTION_LIMIT + self.lookahead_direction_diff
        )

    def calc_fastlane_reward(self, lookwayahead_angle):
        self.fast_lane = False

        self.lookwayahead_direction_diff = Reward.get_direction_diff(
            lookwayahead_angle, self.heading
        )

        if self.lookwayahead_direction_diff <= Reward.FASTLANE_DIRECTION_LIMIT:
            self.fast_lane = True
            self.calc_direction_reward(lookwayahead_angle)
            self.direction_reward *= 2

    def calc_steering_reward(self, power=1):
        if self.fast_lane:
            power = 2

        self.steering_reward = MAX_STEERING / (
            MAX_STEERING + math.pow(self.steering, power)
        )

    def calc_speed_reward(self, immediate_angle, lookahead_angle):
        self.slowdown = False

        self.speed_reward = self.speed / MAX_SPEED

        if self.fast_lane:
            self.speed_reward *= 2

        immediate_vs_lookahead = Reward.get_direction_diff(
            immediate_angle, lookahead_angle
        )

        if (
            immediate_vs_lookahead >= Reward.SLOWDOWN_DIRECTION_LIMIT
            and not self.fast_lane
        ):
            self.slowdown = True

            # cut down the speed reward based on how much direction diff it is
            direction_diff_check = min(MAX_STEERING, immediate_vs_lookahead)
            self.speed_reward = (
                self.speed_reward * MAX_STEERING / (direction_diff_check + MAX_STEERING)
            )

            self.calc_steering_reward(0.5)

    def calc_progress_reward(self, factor):
        self.progress_reward = 0.001

        if self.steps > 5:
            self.progress_reward = factor * self.progress / self.steps

    def calc_lane_reward(self):
        self.lane_reward = 1

        if self.slowdown:
            if self.turn_direction == "left":
                if self.is_left:
                    self.lane_reward += self.border_reward
                else:
                    self.lane_reward = 0
            elif self.turn_direction == "right":
                if not self.is_left:
                    self.lane_reward += self.border_reward
                else:
                    self.lane_reward = 0

    def get_all_rewards(self, display=False):
        if display:
            print(f"direction_reward: {self.direction_reward}")
            print(f"steering_reward: {self.steering_reward}")
            print(f"speed_reward: {self.speed_reward}")
            print(f"progress_reward: {self.progress_reward}")
            print(f"lane_reward: {self.lane_reward}")
        total_rewards = (
            self.direction_reward
            + self.steering_reward
            + self.speed_reward
            + self.progress_reward
            + self.lane_reward
        )

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
    # elif (speed >= MAX_SPEED * 0.9 and steering >= MAX_STEERING / 4) or (
    #     speed <= MIN_SPEED * 1.25 and steering <= MAX_STEERING / 3
    # ):
    #     rewards = 0
    else:
        # Read input variables
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        heading = params["heading"]
        is_left = params["is_left_of_center"]
        track_width = params["track_width"]
        distance_from_center = params["distance_from_center"]
        steps = params["steps"]
        progress = params["progress"]
        # all_wheels_on_track = params["all_wheels_on_track"]

        track = Track(closest_waypoints, waypoints, heading)
        (
            lookwayahead_angle,
            lookahead_angle,
            immediate_angle,
            turn_direction,
        ) = track.get_track_data()

        reward = Reward(
            heading,
            speed,
            steering,
            steering_angle,
            is_left,
            distance_from_center,
            track_width,
            progress,
            steps,
            turn_direction,
        )

        reward.calc_direction_reward(lookahead_angle)
        reward.calc_fastlane_reward(lookwayahead_angle)
        reward.calc_steering_reward()
        reward.calc_speed_reward(immediate_angle, lookahead_angle)
        # this factor is depending on the track itself. 82 * 3 is optimal steps to complete the track
        reward.calc_progress_reward(3)
        reward.calc_lane_reward()

        rewards = reward.get_all_rewards()

    return float(rewards)
