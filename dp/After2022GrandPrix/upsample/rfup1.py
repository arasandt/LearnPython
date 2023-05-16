import math

TRACK_SPLIT = 2
MAX_SPEED = 4.0
# waypoints. do not change as this will affect u-turn angle check.
LOOKAHEAD_COVERAGE = 40
# when to consider uturn for immediate angle
UTURN_THRESHOLD_DEGREE = 110


class Waypoints:
    def __init__(self):
        self.is_upsampled = False

    def dist(self, x, y):
        return math.sqrt((x[0] - y[0]) ** 2 + (x[1] - y[1]) ** 2)

    def up_sample(self, waypoints, k):
        self.is_upsampled = True
        self.original_waypoints = waypoints
        p = self.original_waypoints
        n = len(p)
        self.waypoints = [
            [
                i / k * p[(j + 1) % n][0] + (1 - i / k) * p[j][0],
                i / k * p[(j + 1) % n][1] + (1 - i / k) * p[j][1],
            ]
            for j in range(n)
            for i in range(k)
        ]

    def get_waypoints(self):
        return self.waypoints

    def get_closest_waypoints(self, x, y, closest_waypoints):
        new_closest_waypoints = [0, 0]

        coor_behind_original = self.original_waypoints[closest_waypoints[0]]
        coor_ahead_original = self.original_waypoints[closest_waypoints[1]]
        distance_original = self.dist(coor_behind_original, coor_ahead_original)

        distance_behind_current = self.dist((coor_behind_original), (x, y))

        if distance_behind_current < distance_original / TRACK_SPLIT:
            new_closest_waypoints[0] = closest_waypoints[0] * TRACK_SPLIT
            new_closest_waypoints[1] = (new_closest_waypoints[0] + 1) % len(
                self.waypoints
            )
        else:
            new_closest_waypoints[1] = closest_waypoints[1] * TRACK_SPLIT
            new_closest_waypoints[0] = new_closest_waypoints[1] - 1

        return new_closest_waypoints


wp = Waypoints()


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
        self.closest_waypoints = closest_waypoints
        self.waypoints = waypoints
        self.MAX_WAYPOINT = len(self.waypoints) - 2

    def get_track_data(self):
        # Get upcoming waypoints and their coordinates from current position
        upcoming_waypoints = [
            self.get_next_waypoint(self.closest_waypoints[1], point)
            for point in range(LOOKAHEAD_COVERAGE + 1)
        ]

        upcoming_coordinates = [self.waypoints[point] for point in upcoming_waypoints]

        # Get angle between each proceeding waypoint with upcoming ones
        upcoming_angles = {}
        for count, coor1 in enumerate(upcoming_coordinates):
            angles = []
            for coor2 in upcoming_coordinates[count::]:
                angle = get_angle_between_coordinates(coor1, coor2)
                angles.append(angle)
            upcoming_angles[count] = angles

        track_data = {}
        for count, point in enumerate(upcoming_waypoints):
            track_data[count] = {
                "waypoint": point,
                "coordinates": upcoming_coordinates[count],
                "angles": upcoming_angles[count],
            }

        # Get angle for current waypoint 0 and 1
        current_coordinates = self.waypoints[self.closest_waypoints[0]]
        current_angle = get_angle_between_coordinates(
            self.waypoints[self.closest_waypoints[0]],
            track_data[0]["coordinates"],
        )
        track_data["p0"] = {
            "waypoint": self.closest_waypoints[0],
            "coordinates": current_coordinates,
            "angles": [current_angle],  # its actually angle from p0 to p1
        }

        # Get the angle from waypoint 1 to lookbehind waypoint
        lookbehind_waypoint = self.get_prev_waypoint(
            self.closest_waypoints[1], 5 * TRACK_SPLIT
        )
        lookbehind_angle = get_angle_between_coordinates(
            track_data[0]["coordinates"],
            self.waypoints[lookbehind_waypoint],
        )
        track_data["p99"] = {
            "waypoint": lookbehind_waypoint,
            "coordinates": self.waypoints[lookbehind_waypoint],
            "angles": [lookbehind_angle],
        }
        # check whether on a u-turn between lookbehind and lookahead
        track_data["uturn"] = get_direction_diff(
            lookbehind_angle,
            track_data[0]["angles"][5 * TRACK_SPLIT],
        )

        return track_data


class Reward:
    DIRECTION_LIMIT = 30

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
        steps,
        progress,
        heading_coordinates,
        track_data,
    ):
        self.heading = heading
        self.speed = speed
        self.steering = steering
        self.steering_angle = steering_angle
        self.is_left = is_left
        self.all_wheels_on_track = all_wheels_on_track
        self.steps = steps
        self.progress = progress
        self.heading_coordinates = heading_coordinates
        self.track_data = track_data

        self.midline_reward = (0.5 * track_width) / (
            distance_from_center + 0.5 * track_width
        )
        self.border_reward = 1 - self.midline_reward

        self.off_track = False

        self.uturn = False
        self.uturn_angle = int(self.track_data["uturn"])
        if self.uturn_angle < UTURN_THRESHOLD_DEGREE:
            self.uturn = True

        uturn_direction_angle_one = get_angle_between_coordinates(
            self.track_data["p99"]["coordinates"], self.track_data[0]["coordinates"]
        )
        uturn_direction_angle_two = get_angle_between_coordinates(
            self.track_data["p99"]["coordinates"],
            self.track_data[5 * TRACK_SPLIT]["coordinates"],
        )
        self.turn_direction_uturn = self.get_turn_direction(
            uturn_direction_angle_one, uturn_direction_angle_two
        )
        self.revised_direction = uturn_direction_angle_two

    def calc_direction_reward(self):
        steering_error = 0

        self.direction_diff = get_direction_diff(
            self.track_data[0]["angles"][1],
            self.revised_direction,
        )

        if self.steering > (self.direction_diff / 2):
            steering_error = self.steering - (self.direction_diff / 2)

        self.correct_direction_angle_diff = get_direction_diff(
            self.heading, self.revised_direction
        )

        self.direction_reward = Reward.DIRECTION_LIMIT / (
            Reward.DIRECTION_LIMIT + self.correct_direction_angle_diff + steering_error
        )

    def calc_speed_reward(self):
        self.speed_reward = self.direction_reward * self.speed / MAX_SPEED

    def calc_lane_reward(self):
        self.lane_reward = 1

        if self.uturn:
            if (self.turn_direction_uturn == "left" and self.is_left) or (
                self.turn_direction_uturn == "right" and not self.is_left
            ):
                self.lane_reward = min(1, self.border_reward * 2)
                self.speed_reward = 1
            else:
                self.off_track = True

    def calc_progress_reward(self, factor):
        self.progress_reward = 0.001

        if self.steps > 5:
            self.progress_reward = factor * self.progress / self.steps

    def get_all_rewards(self, display=False):
        if self.off_track:
            return 0

        if display:
            print(f"direction_reward: {self.direction_reward}")
            print(f"speed_reward: {self.speed_reward}")
            print(f"lane_reward: {self.lane_reward}")
            print(f"progress_reward: {self.progress_reward}")
        total_rewards = (
            self.direction_reward
            + self.speed_reward
            + self.lane_reward
            + self.progress_reward
        )

        return total_rewards


def reward_function(params):
    steering_angle = params["steering_angle"]
    steering = abs(steering_angle)
    speed = params["speed"]

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        rewards = 0
    else:
        heading = params["heading"]
        x = params["x"]
        y = params["y"]
        a = x + (2 * math.cos(math.radians(heading)))
        b = y + (2 * math.sin(math.radians(heading)))
        heading_coordinates = {"xy": (x, y), "ab": (a, b)}

        if wp.is_upsampled:
            waypoints = wp.get_waypoints()
        else:
            waypoints = params["waypoints"]
            wp.up_sample(waypoints, TRACK_SPLIT)
            waypoints = wp.get_waypoints()

        closest_waypoints = params["closest_waypoints"]
        closest_waypoints = wp.get_closest_waypoints(x, y, closest_waypoints)

        # Read input variables
        is_left = params["is_left_of_center"]
        track_width = params["track_width"]
        distance_from_center = params["distance_from_center"]
        all_wheels_on_track = params["all_wheels_on_track"]
        steps = params["steps"]
        progress = params["progress"]

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
            steps,
            progress,
            heading_coordinates,
            track_data,
        )

        reward.calc_direction_reward()
        # reward.calc_steering_reward()
        reward.calc_speed_reward()
        reward.calc_lane_reward()
        # this factor is depending on the track itself. 82 * 3 is optimal steps to complete the track
        reward.calc_progress_reward(3)

        rewards = reward.get_all_rewards()

    return float(rewards)
