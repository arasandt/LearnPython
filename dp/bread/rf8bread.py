import math, time

MAX_STEERING = 30
MAX_SPEED = 4.0
CORRECT_LANE_THRESHOLD_DEGREE = 108
DIRECTION_LOOKAHEAD = 8
# waypoints. do not change as this will affect u-turn angle check.
# when to consider uturn for immediate angle
LOOKAHEAD_COVERAGE = int(DIRECTION_LOOKAHEAD * 2.5)


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

    try:
        # From Cosine law
        alpha = math.acos((b2 + c2 - a2) / (2 * b * c))
        betta = math.acos((a2 + c2 - b2) / (2 * a * c))
        gamma = math.acos((a2 + b2 - c2) / (2 * a * b))
    except Exception as error:
        print(A, B, C)
        raise error
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

        for points_behind in [DIRECTION_LOOKAHEAD, DIRECTION_LOOKAHEAD // 2]:
            # Get the angle from waypoint 1 to lookbehind waypoint
            lookbehind_waypoint = self.get_prev_waypoint(
                self.closest_waypoints[1], points_behind
            )
            lookbehind_angle = get_angle_between_coordinates(
                track_data[0]["coordinates"],
                self.waypoints[lookbehind_waypoint],
            )
            point = "p" + str(points_behind)
            track_data[point] = {
                "waypoint": lookbehind_waypoint,
                "coordinates": self.waypoints[lookbehind_waypoint],
                "angles": [lookbehind_angle],
            }

        return track_data


class Reward:
    DIRECTION_LIMIT = 100

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

    def get_angle_and_turn(self, current_coordinate, mid_coordinate, last_coordinate):
        angle = get_upcoming_angle(current_coordinate, mid_coordinate, last_coordinate)
        first_angle = get_angle_between_coordinates(current_coordinate, mid_coordinate)
        second_angle = get_angle_between_coordinates(
            current_coordinate, last_coordinate
        )
        turn_direction = self.get_turn_direction(first_angle, second_angle)

        return angle, turn_direction

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
        self.track_width = track_width
        self.all_wheels_on_track = all_wheels_on_track
        self.steps = steps
        self.progress = progress
        self.heading_coordinates = heading_coordinates
        self.track_data = track_data

        self.midline_reward = (0.5 * track_width) / (
            distance_from_center + 0.5 * track_width
        )
        self.border_reward = 1 - self.midline_reward

        ##### DIRECTION STARTS #####
        actual_direction = int(DIRECTION_LOOKAHEAD)
        self.revised_direction = self.track_data[0]["angles"][actual_direction]

        self.current_angle, self.current_angle_turn_direction = self.get_angle_and_turn(
            self.track_data["p" + str(actual_direction)]["coordinates"],
            self.track_data[0]["coordinates"],
            self.track_data[actual_direction]["coordinates"],
        )
        (
            self.upcoming_angle,
            self.upcoming_angle_turn_direction,
        ) = self.get_angle_and_turn(
            self.track_data[0]["coordinates"],
            self.track_data[actual_direction]["coordinates"],
            self.track_data[actual_direction * 2]["coordinates"],
        )
        ##### DIRECTION ENDS #####

    def calc_direction_reward(self):
        self.direction_reward = 0

        self.correct_direction_angle_diff = get_direction_diff(
            self.heading, self.revised_direction
        )

        self.direction_error = (
            1 - self.correct_direction_angle_diff / Reward.DIRECTION_LIMIT
        )

    def calc_speed_reward(self):
        # current_weight = 1 - self.current_angle / 180
        # upcoming_weight = 1 - self.upcoming_angle / 180

        # direction_weight = current_weight + upcoming_weight
        # direction_weight *= 3
        direction_weight = 2

        self.speed_reward = (
            math.pow(abs(self.direction_error), direction_weight)
            * self.speed
            / MAX_SPEED
        )

        if self.direction_error < 0:
            self.speed_reward = 0

    def calc_lane_reward(self):
        self.lane_reward = 1

        if self.current_angle < CORRECT_LANE_THRESHOLD_DEGREE:
            if (self.current_angle_turn_direction == "left" and self.is_left) or (
                self.current_angle_turn_direction == "right" and not self.is_left
            ):
                self.lane_reward = 1
            else:
                self.lane_reward = 0

    def get_all_rewards(self, display=False):
        total_rewards = self.direction_reward + self.speed_reward + self.lane_reward

        if display:
            print("waypoint:", self.track_data[0]["waypoint"])
            print(f"current_angle: {self.current_angle}")
            print(f"upcoming_angle: {self.upcoming_angle}")
            print(f"heading: {self.heading}")
            print(f"revised_direction: {self.revised_direction}")
            print(f"direction_error: {self.direction_error}")
            print(f"direction_reward: {self.direction_reward}")
            print(f"speed_reward: {self.speed_reward}")
            print(f"total_rewards: {total_rewards}")
            print(f"lane_reward: {self.lane_reward}")

        if self.lane_reward == 0:
            total_rewards = 0

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
        reward.calc_lane_reward()

        rewards = reward.get_all_rewards()

    return float(rewards)
