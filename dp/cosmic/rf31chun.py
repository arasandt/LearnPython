import math, time

MAX_STEERING = 30
MAX_SPEED = 4.0
# waypoints. do not change as this will affect u-turn angle check.
LOOKAHEAD_COVERAGE = 20
# when to consider uturn for immediate angle
UTURN_THRESHOLD_DEGREE = 110
DIRECTION_LOOKAHEAD = 5


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


def get_upcoming_angle(A, B, C):
    def lengthSquare(X, Y):
        xDiff = X[0] - Y[0]
        yDiff = X[1] - Y[1]
        return xDiff * xDiff + yDiff * yDiff

    # Square of lengths be a2, b2, c2
    a2 = lengthSquare(B, C)
    b2 = lengthSquare(A, C)
    c2 = lengthSquare(A, B)

    # length of sides be a, b, c
    a = math.sqrt(a2)
    b = math.sqrt(b2)
    c = math.sqrt(c2)

    # From Cosine law
    alpha = math.acos((b2 + c2 - a2) / (2 * b * c))
    betta = math.acos((a2 + c2 - b2) / (2 * a * c))
    gamma = math.acos((a2 + b2 - c2) / (2 * a * b))

    # Converting to degree
    alpha = alpha * 180 / math.pi
    betta = betta * 180 / math.pi
    gamma = gamma * 180 / math.pi

    return betta


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
            self.closest_waypoints[1], DIRECTION_LOOKAHEAD
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
            track_data[0]["angles"][DIRECTION_LOOKAHEAD],
        )

        return track_data


class Reward:
    DIRECTION_LIMIT = 60

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

        self.uturn = False
        self.uturn_angle = int(self.track_data["uturn"])
        if self.uturn_angle < UTURN_THRESHOLD_DEGREE:
            self.uturn = True

        uturn_direction_angle_one = get_angle_between_coordinates(
            self.track_data["p99"]["coordinates"], self.track_data[0]["coordinates"]
        )
        uturn_direction_angle_two = get_angle_between_coordinates(
            self.track_data["p99"]["coordinates"],
            self.track_data[DIRECTION_LOOKAHEAD]["coordinates"],
        )
        self.turn_direction_uturn = self.get_turn_direction(
            uturn_direction_angle_one, uturn_direction_angle_two
        )
        self.revised_direction = self.track_data[0]["angles"][DIRECTION_LOOKAHEAD]

    def calc_direction_reward(self):
        direction_limit = 1.5
        steering_error = 0

        self.direction_diff = get_direction_diff(
            self.track_data[0]["angles"][1],
            self.revised_direction,
        )
        current_coordinate = self.track_data[0]["coordinates"]
        five_coordinate = self.track_data[DIRECTION_LOOKAHEAD]["coordinates"]
        ten_coordinate = self.track_data[DIRECTION_LOOKAHEAD * 2]["coordinates"]
        self.upcoming_angle = get_upcoming_angle(
            current_coordinate, five_coordinate, ten_coordinate
        )
        self.upcoming_angle = max(
            self.upcoming_angle - self.direction_diff + direction_limit, 0
        )
        self.upcoming_angle = min(self.upcoming_angle, 180)

        self.turn_direction = self.get_turn_direction(
            self.track_data[0]["angles"][1], self.revised_direction
        )
        self.correct_direction_angle_diff = get_direction_diff(
            self.heading, self.revised_direction
        )

        # direction limit gives some freedom for training to decide the angle
        if self.correct_direction_angle_diff <= direction_limit:
            self.correct_direction_angle_diff = 0

        if self.turn_direction == "right" and self.steering_angle > direction_limit:
            steering_error = abs(self.steering_angle - direction_limit)
        elif self.turn_direction == "left" and self.steering_angle < -direction_limit:
            steering_error = abs(self.steering_angle + direction_limit)

        if self.steering > self.direction_diff and self.steering > direction_limit:
            steering_error += self.steering - self.direction_diff

        if self.correct_direction_angle_diff >= Reward.DIRECTION_LIMIT:
            self.direction_reward_main = 0.01
        else:
            self.direction_reward_main = (
                1 - self.correct_direction_angle_diff / Reward.DIRECTION_LIMIT
            )

        if steering_error >= Reward.DIRECTION_LIMIT:
            self.direction_reward_steering = 0.01
        else:
            self.direction_reward_steering = 1 - steering_error / Reward.DIRECTION_LIMIT

        self.direction_reward_final = (self.direction_reward_main * 0.5) + (
            self.direction_reward_steering * 0.5
        )

        self.direction_reward = self.direction_reward_final / math.pow(
            self.upcoming_angle / 180, 1.33
        )

    def calc_speed_reward(self):
        self.speed_reward = (
            math.pow(self.direction_reward_final, 2) * self.speed / MAX_SPEED
        )

    def get_all_rewards(self, display=False):
        if display:
            print(f"direction_reward: {self.direction_reward}")
            print(f"speed_reward: {self.speed_reward}")
        total_rewards = self.direction_reward + self.speed_reward

        return total_rewards


def reward_function(params):
    steering_angle = params["steering_angle"]
    steering = abs(steering_angle)
    speed = params["speed"]

    ######## Check #1 - OFFTRACK / REVERSE CHECK ########
    if params["is_offtrack"] or params["is_reversed"]:
        rewards = 0
    else:
        # Read input variables
        waypoints = params["waypoints"]
        closest_waypoints = params["closest_waypoints"]
        heading = params["heading"]
        is_left = params["is_left_of_center"]
        track_width = params["track_width"]
        distance_from_center = params["distance_from_center"]
        all_wheels_on_track = params["all_wheels_on_track"]
        steps = params["steps"]
        progress = params["progress"]
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
            steps,
            progress,
            heading_coordinates,
            track_data,
        )

        reward.calc_direction_reward()
        reward.calc_speed_reward()

        rewards = reward.get_all_rewards()

    return float(rewards)
