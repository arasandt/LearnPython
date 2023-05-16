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


def get_direction_diff(first_direction, second_direction):
    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(first_direction - second_direction)

    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    return direction_diff


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

        # Get upcoming waypoints and their coordinates from current posittion
        upcoming_waypoints = [
            self.get_next_waypoint(self.closest_waypoints[1], point)
            for point in self.lookahead_waypoints
        ]
        upcoming_coordinates = [self.waypoints[point] for point in upcoming_waypoints]

        # Get angle between waypoint 1 to each of the upcoming waypoints
        upcoming_angles = []
        for coor in upcoming_coordinates:
            angle = get_angle_between_coordinates(
                self.waypoints[self.closest_waypoints[1]], coor
            )
            upcoming_angles.append(angle)

        # Get angle for current waypoint 0 and 1
        current_coordinates_0 = self.waypoints[self.closest_waypoints[0]]
        current_coordinates_1 = self.waypoints[self.closest_waypoints[1]]
        current_angle = get_angle_between_coordinates(
            self.waypoints[self.closest_waypoints[0]],
            self.waypoints[self.closest_waypoints[1]],
        )

        # Get the angle from waypoint 1 to lookbehind waypoint
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

        # check whether on a u-turn between lookbehind and lookahead
        track_data["uturn"] = get_direction_diff(
            lookbehind_angle,
            upcoming_angles[4],
        )

        # check whether there is a uturn upcoming between lookahead and lookwayahead
        upcoming_uturn_line2 = get_angle_between_coordinates(
            upcoming_coordinates[9],
            upcoming_coordinates[4],
        )
        track_data["upcominguturn"] = get_direction_diff(
            upcoming_angles[4],
            upcoming_uturn_line2,
        )

        return track_data


class Reward:

    DIRECTION_LIMIT = 30
    # since the index starts from 0, lookahead includes 0 as well.
    LOOKAHEAD = (LOOKAHEAD_COVERAGE // 2) - 1

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
        all_wheels_on_track,
        heading_coordinates,
        track_data,
    ):
        self.heading = heading
        self.speed = speed
        self.steering = steering
        self.steering_angle = steering_angle
        self.is_left = is_left
        self.all_wheels_on_track = all_wheels_on_track
        self.heading_coordinates = heading_coordinates
        self.track_data = track_data

        self.midline_reward = (0.5 * track_width) / (
            distance_from_center + 0.5 * track_width
        )
        self.border_reward = 1 - self.midline_reward

        self.slow = False
        if int(self.track_data["uturn"]) < 110:
            self.slow = True

        self.upcoming_slow = False
        self.upcoming_median = False
        if int(self.track_data["upcominguturn"]) < 110:
            self.upcoming_slow = True
        elif int(self.track_data["upcominguturn"]) < 130:
            self.upcoming_median = True

    def calc_direction_reward(self):
        direction_limit = 3
        self.direction_reward = 1

        if self.upcoming_slow:
            default_waypoint = 0
        elif self.upcoming_median:
            self.direction_reward = 1.5
            default_waypoint = LOOKAHEAD_COVERAGE // 2 - 1
        else:
            default_waypoint = LOOKAHEAD_COVERAGE - 1

        self.correct_turn_direction = self.get_turn_direction(
            self.track_data["p0"]["angle_from_p1"],
            self.track_data[default_waypoint]["angle_from_p1"],
        )
        self.correct_direction_angle_diff = get_direction_diff(
            self.heading,
            self.track_data[default_waypoint]["angle_from_p1"],
        )

        if self.correct_direction_angle_diff > direction_limit:
            self.direction_reward = Reward.DIRECTION_LIMIT / (
                Reward.DIRECTION_LIMIT + self.correct_direction_angle_diff
            )

    def calc_steering_reward(self, power=1):
        self.steering_reward = MAX_STEERING / (
            MAX_STEERING + math.pow(self.steering, power)
        )

    def calc_speed_reward(self):
        self.speed_reward = 2 * self.speed / (MAX_SPEED + self.speed)

        # for 3, have 2.5, for 4 have it as 3. Formula will take care of it.
        slow_speed = (MAX_SPEED + MIN_SPEED) / (1 + MAX_SPEED / 2)
        speed_diff = abs(slow_speed - self.speed)
        self.slow_speed_reward = slow_speed / (slow_speed + speed_diff)

    def slow_down(self):
        self.speed_reward = self.slow_speed_reward
        self.calc_steering_reward(0.5)

    def calc_lane_reward(self):
        self.lane_reward = 1

        if self.slow:
            self.lane_reward = 0
            self.slow_down()

            # slowdown and then check the lane
            if (self.correct_turn_direction == "left" and self.is_left) or (
                self.correct_turn_direction == "right" and not self.is_left
            ):
                self.lane_reward += self.border_reward

                if not self.all_wheels_on_track:
                    self.lane_reward += 0.2

    def get_all_rewards(self, display=False):
        if display:
            print(f"direction_reward: {self.direction_reward}")
            print(f"steering_reward: {self.steering_reward}")
            print(f"speed_reward: {self.speed_reward}")
            print(f"lane_reward: {self.lane_reward}")
        total_rewards = (
            self.direction_reward
            + self.steering_reward
            + self.speed_reward
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
            all_wheels_on_track,
            heading_coordinates,
            track_data,
        )

        reward.calc_direction_reward()
        reward.calc_steering_reward()
        reward.calc_speed_reward()
        # this factor is depending on the track itself. 82 * 3 is optimal steps to complete the track
        reward.calc_lane_reward()

        rewards = reward.get_all_rewards()

    return float(rewards)
