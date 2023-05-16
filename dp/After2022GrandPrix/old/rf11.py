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
# waypoints. do not change as this will affect u-turn angle check.
LOOKAHEAD_COVERAGE = 10


def get_angle_between_coordinates(current_coor, next_coor):
    # Calculate the direction in radius, arctan2(dy, dx),
    angle = math.atan2(next_coor[1] - current_coor[1], next_coor[0] - current_coor[0])
    # Convert to degree
    return math.degrees(angle)


class Track:
    def get_next_waypoint(self, point, next_waypoint):
        new_next_waypoint = point + next_waypoint
        if new_next_waypoint > self.MAX_WAYPOINT:
            new_next_waypoint = new_next_waypoint - self.MAX_WAYPOINT - 1
        return new_next_waypoint

    def get_prev_waypoint(self, point, prev_waypoint):
        new_prev_waypoint = point - prev_waypoint
        if new_prev_waypoint < 0:
            new_prev_waypoint = new_prev_waypoint + self.MAX_WAYPOINT + 1
        return new_prev_waypoint

    def __init__(self, closest_waypoints, waypoints):

        self.lookahead_waypoints = list(range(1, LOOKAHEAD_COVERAGE + 1))
        self.closest_waypoints = closest_waypoints
        self.waypoints = waypoints
        self.MAX_WAYPOINT = len(self.waypoints) - 1

    def get_track_data(self):

        upcoming_waypoints = [
            self.get_next_waypoint(self.closest_waypoints[1], point)
            for point in self.lookahead_waypoints
        ]
        upcoming_coordinates = [self.waypoints[point] for point in upcoming_waypoints]

        upcoming_angles = []
        for coor in upcoming_coordinates:
            angle = get_angle_between_coordinates(
                self.waypoints[self.closest_waypoints[1]], coor
            )
            upcoming_angles.append(angle)

        current_coordinates_0 = self.waypoints[self.closest_waypoints[0]]
        current_coordinates_1 = self.waypoints[self.closest_waypoints[1]]
        current_angle = get_angle_between_coordinates(
            self.waypoints[self.closest_waypoints[0]],
            self.waypoints[self.closest_waypoints[1]],
        )

        lookbehind_waypoint = self.get_prev_waypoint(
            self.closest_waypoints[1], LOOKAHEAD_COVERAGE // 2
        )
        lookbehind_angle = get_angle_between_coordinates(
            self.waypoints[self.closest_waypoints[1]],
            self.waypoints[lookbehind_waypoint],
        )

        track_data = {}
        for count, point in enumerate(upcoming_waypoints):
            track_data[count] = {
                "waypoint": point,
                "coordinates": upcoming_coordinates[count],
                "angle_from_p1": upcoming_angles[count],
            }

        track_data["p0"] = {
            "waypoint": self.closest_waypoints[0],
            "coordinates": current_coordinates_0,
            "angle_from_p1": current_angle,  # its actually angle from p0 to p1
        }

        track_data["p1"] = {
            "waypoint": self.closest_waypoints[1],
            "coordinates": current_coordinates_1,
            "angle_from_p1": 0,
        }

        track_data["p99"] = {
            "waypoint": lookbehind_waypoint,
            "coordinates": self.waypoints[lookbehind_waypoint],
            "angle_from_p1": lookbehind_angle,
        }

        return track_data


class Reward:

    DIRECTION_LIMIT = 30
    # since the index starts from 0, lookahead includes 0 as well.
    LOOKAHEAD = 3

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
        heading_coordinates,
        track_data,
    ):
        self.heading = heading
        self.speed = speed
        self.steering = steering
        self.steering_angle = steering_angle
        self.is_left = is_left
        self.progress = progress
        self.steps = steps
        self.all_wheels_on_track = all_wheels_on_track
        self.heading_coordinates = heading_coordinates
        self.track_data = track_data

        # self.lookahead_angle = self.track_data[self.LOOKAHEAD]["angle_from_p1"]
        # self.lookahead_angle_ahead = self.track_data[self.LOOKAHEAD * 2][
        #     "angle_from_p1"
        # ]

        self.midline_reward = (0.5 * track_width) / (
            distance_from_center + 0.5 * track_width
        )
        self.border_reward = 1 - self.midline_reward

        self.upcoming_directions_from_heading()

    @staticmethod
    def get_direction_diff(first_direction, second_direction):
        # Calculate the difference between the track direction and the heading direction of the car
        direction_diff = abs(first_direction - second_direction)

        if direction_diff > 180:
            direction_diff = 360 - direction_diff

        return direction_diff

    @staticmethod
    def direction_and_angle_between_two_lines(last_center, last, nex_center, nex):
        Xfactor = min(last_center[0], last[0], nex_center[0], nex[0])
        Yfactor = min(last_center[1], last[1], nex_center[1], nex[1])

        new_last_center = (last_center[0] - Xfactor, last_center[1] - Yfactor)
        new_last = (last[0] - Xfactor, last[1] - Yfactor)
        new_nex_center = (nex_center[0] - Xfactor, nex_center[1] - Yfactor)
        new_nex = (nex[0] - Xfactor, nex[1] - Yfactor)

        first_line = get_angle_between_coordinates(new_last_center, new_last)
        second_line = get_angle_between_coordinates(new_nex_center, new_nex)

        angle = Reward.get_direction_diff(first_line, second_line)

        if first_line > second_line:
            return ("right", angle)
        elif first_line < second_line:
            return ("left", angle)
        else:
            return ("straight", angle)

    def upcoming_directions_from_heading(self):
        self.upcoming_directions = {}

        for count in range(LOOKAHEAD_COVERAGE):
            direction, direction_angle = self.direction_and_angle_between_two_lines(
                self.heading_coordinates["xy"],
                self.heading_coordinates["ab"],
                self.heading_coordinates["xy"],
                self.track_data[count]["coordinates"],
            )
            self.upcoming_directions[count] = {
                "count": count,
                "direction": direction,
                "direction_angle": direction_angle,
            }

    def calc_direction_reward(self):
        direction_limit = 3

        angles_within_threshold = [
            self.upcoming_directions[i]
            for i in range(self.LOOKAHEAD, self.LOOKAHEAD * 2 + 1)
            if self.upcoming_directions[i]["direction_angle"] <= direction_limit
        ]

        self.correct_turn_direction = self.upcoming_directions[self.LOOKAHEAD][
            "direction"
        ]
        self.correct_direction_angle_diff = self.upcoming_directions[self.LOOKAHEAD][
            "direction_angle"
        ]
        self.direction_reward_factor = 1

        temp_count = 0
        selected_item = None

        for item in angles_within_threshold:
            if item["count"] > temp_count:
                temp_count = item["count"]
                selected_item = item

        if selected_item is not None:
            self.correct_turn_direction = selected_item["direction"]
            self.correct_direction_angle_diff = selected_item["direction_angle"]
            self.direction_reward_factor = selected_item["count"] / self.LOOKAHEAD

        self.direction_reward = Reward.DIRECTION_LIMIT / (
            Reward.DIRECTION_LIMIT + self.correct_direction_angle_diff
        )
        self.direction_reward *= self.direction_reward_factor

        self.turn_direction = Reward.get_turn_direction(
            self.track_data["p0"]["angle_from_p1"],
            self.track_data[self.LOOKAHEAD]["angle_from_p1"],
        )

    def calc_steering_reward(self, power=1):
        self.steering_reward = MAX_STEERING / (
            MAX_STEERING + math.pow(self.steering, power)
        )

    def calc_speed_reward(self):
        self.speed_reward = 2 * self.speed / (MAX_SPEED + self.speed)

        # for 3, have 2.5, for 4 have it as 3. Formaula will take care of it.
        slow_speed = (MAX_SPEED + MIN_SPEED) / (1 + MAX_SPEED / 2)
        speed_diff = abs(slow_speed - self.speed)
        self.slow_speed_reward = slow_speed / (slow_speed + speed_diff)

    def calc_progress_reward(self, factor):
        self.progress_reward = 0.001

        if self.steps > 5:
            self.progress_reward = factor * self.progress / self.steps
            if self.progress == 100:
                self.progress_reward *= 1.5

    def slow_down(self):
        self.speed_reward = self.slow_speed_reward
        self.calc_steering_reward(0.5)

    def calc_lane_reward(self):
        self.lane_reward = 1

        slow_direction_diff = Reward.get_direction_diff(
            self.track_data["p99"]["angle_from_p1"],
            self.track_data[self.LOOKAHEAD + 1]["angle_from_p1"],
        )

        if slow_direction_diff <= 90:
            self.lane_reward = 0

            if (self.turn_direction == "left" and self.is_left) or (
                self.turn_direction == "right" and not self.is_left
            ):
                self.lane_reward += self.border_reward

                if not self.all_wheels_on_track:
                    self.lane_reward += 0.2

                # cut down the speed reward only if it's a u-turn scenario
                # if slow_direction_diff <= 90:
                self.slow_down()

        # elif self.lookahead_direction_diff >= 45:
        #     self.slow_down()

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
        x = params["x"]
        y = params["y"]
        a = x + (2 * math.cos(math.radians(heading)))
        b = y + (2 * math.sin(math.radians(heading)))
        heading_coordinates = {"xy": (x, y), "ab": (a, b)}

        track = Track(closest_waypoints, waypoints)
        track_data = track.get_track_data()

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
            heading_coordinates,
            track_data,
        )

        reward.calc_direction_reward()
        reward.calc_steering_reward()
        reward.calc_speed_reward()
        # this factor is depending on the track itself. 82 * 3 is optimal steps to complete the track
        reward.calc_progress_reward(3)
        reward.calc_lane_reward()

        rewards = reward.get_all_rewards()

    return float(rewards)
