import os
import math
import json

expected_track_length = 81
lookahead = 5


def get_next_waypoint(point, next_waypoint):
    new_next_waypoint = point + next_waypoint
    if new_next_waypoint > expected_track_length:
        new_next_waypoint = new_next_waypoint - expected_track_length - 1
    return new_next_waypoint


def get_prev_waypoint(point, prev_waypoint):
    new_prev_waypoint = point - prev_waypoint
    if new_prev_waypoint < 0:
        new_prev_waypoint = new_prev_waypoint + expected_track_length + 1
    return new_prev_waypoint


def format_json(file_name):
    track_data = {}
    with open(file_name, "r") as file:
        data = file.readlines()

    for item in data:
        item = eval(item)
        for k, v in item.items():
            if isinstance(v, dict):
                if v["waypoint"] in track_data:
                    pass
                else:
                    track_data[v["waypoint"]] = v["coordinates"]

    print(len(track_data))
    # print(set(range(1, expected_track_length + 1)).difference(track_data.keys()))
    return track_data


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


def get_revised_direction_discrete(current_coordinate, track_data, lookahead):
    angles = []
    base_angle = ""
    for point, value in track_data.items():
        if isinstance(point, int):
            coor = value["coordinates"]
            angle = get_angle_between_coordinates(current_coordinate, coor)
            if point == 1:
                base_angle = angle
            angles.append(angle)

    angles = angles[1 : lookahead + 1 :]

    angles_diff = [(360 + i) if i < 0 else i for i in angles]
    angles_diff = [i - angles[0] for i in angles_diff]
    angles_diff = [(i - 360) for i in angles_diff]
    angles_diff = [(360 + i) if i <= -180 else i for i in angles_diff]

    average_angle_diff = sum(angles_diff) / len(angles_diff)
    average_angle = angles[0] + average_angle_diff
    if average_angle > 180:
        average_angle -= 360
    elif average_angle <= -180:
        average_angle += 360

    return average_angle, base_angle


def get_revised_direction(current_coordinate, track_data, lookahead=20, limit=30):
    for i in list(range(lookahead + 1))[::-1][:-5:]:
        revised_direction, base_angle = get_revised_direction_discrete(
            current_coordinate, track_data, lookahead=i
        )

        if int(get_direction_diff(revised_direction, base_angle)) <= limit:
            print(i)
            return revised_direction, base_angle
    return limit, base_angle


track_name = "larsloop"
track_data = format_json(f"{track_name}_raw.json")

with open(f"{track_name}.json", "w") as file:
    file.write(json.dumps(track_data))

# print(track_data)


def get_new_track_data(track_data, point):
    new_track_data = {}
    for i in range(16):
        waypoint = get_next_waypoint(point, i)
        new_track_data[i] = {
            "waypoints": waypoint,
            "coordinates": track_data[waypoint],
        }
    return new_track_data


for point in range(expected_track_length + 1):
    # point = 61
    new_track_data = get_new_track_data(track_data, point)
    # print(new_track_data)
    point_coor = new_track_data[0]["coordinates"]
    revised_angle, base_angle = get_revised_direction(point_coor, new_track_data)
    print(
        "waypoint",
        point,
        "base_angle",
        base_angle,
        "revised_angle",
        revised_angle,
        "direction_diff",
        get_direction_diff(base_angle, revised_angle),
    )
    # if point > 50:
    # break
    # break
