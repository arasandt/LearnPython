# Gradient descent batch size	64
# Entropy	0.01
# Discount factor	0.88
# Loss type	mean squared error
# "loss_type": "mean squared error",
# Learning rate	0.0003
# Number of experience episodes between each policy-updating iteration	18
# Number of epochs	4
# Speed: [ 1.2 : 2.0 ] m/s
# Steering angle: [ -15 : 30 ] °
# Training time 4 hours until stoppage

import math

MAX_STEERING = 30
MIN_SPEED, MAX_SPEED = 1.2, 2.0


class Track:
    LOOKWAYAHEAD_WAYPOINT = 8

    def get_next_waypoint(self, point, ahead_waypoint):
        new_next_waypoint = point + ahead_waypoint
        if new_next_waypoint > self.MAX_WAYPOINT:
            new_next_waypoint = new_next_waypoint - self.MAX_WAYPOINT - 1
        return new_next_waypoint

    def get_prev_waypoint(self, point, behind_waypoint):
        new_prev_waypoint = point - behind_waypoint
        if new_prev_waypoint < 0:
            new_prev_waypoint = new_prev_waypoint + self.MAX_WAYPOINT + 1
        return new_prev_waypoint

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

        self.lookahead_waypoints = [
            point
            for point in range(
                self.LOOKWAYAHEAD_WAYPOINT // 2, self.LOOKWAYAHEAD_WAYPOINT + 1
            )
        ][::-1]

        self.closest_waypoints = closest_waypoints
        self.waypoints = waypoints
        self.MAX_WAYPOINT = len(self.waypoints) - 1
        self.heading = heading

    def get_angles(self, next_waypoint):
        angle = Track.get_direction_degree(
            self.waypoints,
            self.closest_waypoints[1],
            self.get_next_waypoint(self.closest_waypoints[1], next_waypoint),
        )

        return angle

    def get_track_data(self):

        all_angles = [self.get_angles(point) for point in self.lookahead_waypoints]

        immediate_angle = Track.get_direction_degree(
            self.waypoints,
            self.closest_waypoints[0],
            self.closest_waypoints[1],
        )

        lookbehind_angle = Track.get_direction_degree(
            self.waypoints,
            self.closest_waypoints[0],
            self.get_prev_waypoint(
                self.closest_waypoints[0], self.LOOKWAYAHEAD_WAYPOINT // 2
            ),
        )

        return all_angles, immediate_angle, lookbehind_angle


class Reward:

    DIRECTION_LIMIT = 30
    FASTLANE_DIRECTION_LIMIT = 6

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
        all_wheels_on_track,
        immediate_angle,
        lookahead_angle,
        lookbehind_angle,
    ):
        self.heading = heading
        self.speed = speed
        self.steering = steering
        self.steering_angle = steering_angle
        self.is_left = is_left
        self.progress = progress
        self.steps = steps
        self.all_wheels_on_track = all_wheels_on_track
        self.immediate_angle = immediate_angle
        self.lookahead_angle = lookahead_angle
        self.lookbehind_angle = lookbehind_angle

        self.midline_reward = (0.5 * track_width) / (
            distance_from_center + 0.5 * track_width
        )
        self.border_reward = 1 - self.midline_reward

    @staticmethod
    def get_direction_diff(first_direction, second_direction):
        # Calculate the difference between the track direction and the heading direction of the car
        direction_diff = abs(first_direction - second_direction)

        if direction_diff > 180:
            direction_diff = 360 - direction_diff

        return direction_diff

    def calc_direction_reward(self):
        self.direction_reward = 1

        self.lookahead_direction_diff = Reward.get_direction_diff(
            self.lookahead_angle, self.heading
        )

        # allow margin for error, which is 3 degree. Looks reasonable for the track.
        if self.lookahead_direction_diff > 3:
            self.direction_reward = Reward.DIRECTION_LIMIT / (
                Reward.DIRECTION_LIMIT + self.lookahead_direction_diff
            )

        self.turn_direction = Reward.get_turn_direction(
            self.immediate_angle, self.lookahead_angle
        )

    def calc_steering_reward(self, power=1):
        self.steering_reward = MAX_STEERING / (
            MAX_STEERING + math.pow(self.steering, power)
        )

    def calc_fastlane_reward(self, all_angles):
        self.fast_lane = False

        all_direction_diff = [
            Reward.get_direction_diff(dd, self.heading) for dd in all_angles[:-3:]
        ]

        self.lookawayhead_direction_diff = all_direction_diff[0]

        lookahead_vs_lookwayahead = Reward.get_direction_diff(
            self.lookahead_angle, all_angles[0]
        )
        if lookahead_vs_lookwayahead <= 3:
            self.direction_reward = 1

        # for count, diff in enumerate(all_direction_diff):
        #     if diff <= Reward.FASTLANE_DIRECTION_LIMIT:
        #         lookwayahead_angle = all_angles[count]
        #         self.fast_lane = True
        #         self.calc_direction_reward(self.immediate_angle, lookwayahead_angle)
        #         self.direction_reward = self.direction_reward * (3 - count * 0.2)
        #         self.calc_steering_reward(2)
        #         break

    def calc_speed_reward(self):
        self.speed_reward = 2 * self.speed / (MAX_SPEED + self.speed)

        if self.fast_lane:
            self.speed_reward *= 2

        # for 3, have 2.5, for 4 have it as 3. Formaula will take care of it.
        slow_speed = (MAX_SPEED + MIN_SPEED) / (1 + MAX_SPEED / 2)
        speed_diff = abs(slow_speed - self.speed)
        self.slow_speed_reward = slow_speed / (slow_speed + speed_diff)

    def calc_progress_reward(self, factor):
        self.progress_reward = 0.001

        if self.steps > 5:
            self.progress_reward = factor * self.progress / self.steps

    def calc_lane_reward(self):
        self.lane_reward = 1

        slow_direction_diff = abs(
            Reward.get_direction_diff(self.lookbehind_angle, self.lookahead_angle)
        )

        if (
            slow_direction_diff <= 90 and not self.fast_lane
        ) or self.lookahead_direction_diff >= 45:
            if self.turn_direction == "left":
                self.lane_reward = 0

                if self.is_left:
                    self.lane_reward += self.border_reward

                    if not self.all_wheels_on_track:
                        self.lane_reward += 0.2

                    # cut down the speed reward only if it's a u-turn scenario
                    if slow_direction_diff <= 90 or self.lookahead_direction_diff >= 45:
                        self.speed_reward = self.slow_speed_reward
                        self.calc_steering_reward(0.5)
            elif self.turn_direction == "right":
                self.lane_reward = 0

                if not self.is_left:
                    self.lane_reward += self.border_reward

                    if not self.all_wheels_on_track:
                        self.lane_reward += 0.2

                    # cut down the speed reward only if it's a u-turn scenario
                    if slow_direction_diff <= 90 or self.lookahead_direction_diff >= 45:
                        self.speed_reward = self.slow_speed_reward
                        self.calc_steering_reward(0.5)

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
        all_wheels_on_track = params["all_wheels_on_track"]

        track = Track(closest_waypoints, waypoints, heading)
        (
            all_angles,
            immediate_angle,
            lookbehind_angle,
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
            all_wheels_on_track,
            immediate_angle,
            all_angles[-1],  # lookahead_angle
            lookbehind_angle,
        )

        reward.calc_direction_reward()
        reward.calc_steering_reward()
        reward.calc_fastlane_reward(all_angles)
        reward.calc_speed_reward()
        # this factor is depending on the track itself. 82 * 3 is optimal steps to complete the track
        reward.calc_progress_reward(3)
        reward.calc_lane_reward()

        rewards = reward.get_all_rewards()

    return float(rewards)
