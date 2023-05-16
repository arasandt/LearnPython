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
        for _, v in item.items():
            if isinstance(v, dict):
                if v["waypoint"] in track_data:
                    pass
                else:
                    track_data[v["waypoint"]] = v["coordinates"]

    print(set(range(1, expected_track_length + 1)).difference(track_data.keys()))
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


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i : i + n]


def get_revised_direction(angles):
    angle_diff = angles[::]
    split_array = list(chunks(angle_diff, 5))[:-1:]
    selected_angle = split_array[0][-1]
    # print(selected_angle)
    if int(max(split_array[0])) < 20:
        found = 0
        for arr in split_array[1:]:
            # print(arr)
            if int(max(arr)) >= 20:
                filter_angle = [i for i in arr if int(i) <= 20]
                if filter_angle:
                    found = 1
                    selected_angle = max(filter_angle)
                break
            # break
        if not found:
            filter_angle = [i for i in angle_diff[5:15:] if int(i) <= 20]
            if filter_angle:
                selected_angle = max(filter_angle)
    else:
        new_angle = [i for i in split_array[1] if i < selected_angle]
        if new_angle:
            selected_angle = min(new_angle)
    location = angles.index(selected_angle)
    return selected_angle, location


track_name = "larsloop"
track_data = format_json(f"{track_name}_raw.json")

with open(f"{track_name}.json", "w") as file:
    file.write(json.dumps(track_data))


prev_waypoint = -1
for point in range(expected_track_length + 1):
    # point = 76
    next_point = get_next_waypoint(point, 7)
    prev_point = get_prev_waypoint(point, 7)
    # print(prev_point, "(", point, ")", next_point)
    a = track_data[point]
    b = track_data[next_point]
    c = track_data[prev_point]
    angle1 = get_angle_between_coordinates(a, b)
    angle2 = get_angle_between_coordinates(a, c)
    result = get_direction_diff(angle1, angle2)
    # print(f"{a},{b} vs {a},{c} : {angle1} vs {angle2}")
    speed = "fast"
    if int(result) <= 100:
        speed = "slow"
    print(prev_point, "(", point, ")", next_point, "       in uturn", result, speed)

    results = []
    for i in range(1, 21):
        if i == 6:
            print("---------------------")
        prev_point = get_prev_waypoint(point, 1)
        next_next_point = get_next_waypoint(point, i)
        a = track_data[prev_point]
        b = track_data[point]
        c = track_data[next_next_point]
        angle1 = get_angle_between_coordinates(a, b)
        angle2 = get_angle_between_coordinates(b, c)
        # print(angle1, angle2)
        result = get_direction_diff(angle1, angle2)
        results.append(result)
        print(
            "(",
            point,
            ")",
            next_point,
            next_next_point,
            "",
            result,
            "",
        )
        # break

    degree, location = get_revised_direction(results)
    # save_waypoint = (point + location + 1) % expected_track_length
    # if prev_waypoint < save_waypoint:
    #     prev_waypoint = save_waypoint
    #     print(f"new anchor {prev_waypoint}")
    # else:
    #     print(f"old anchor {prev_waypoint}")
    # results = results[1::]
    # split = 5
    # degree = 0
    # temp = ""
    # for i in range(4):
    #     temp1 = temp
    #     temp = results[i * split : split * (i + 1) :]
    #     # print(temp)
    #     if max(temp) <= 20:
    #         print(f"{max(temp)}. no 20 degree found first itself. checking next batch")
    #     elif max(temp) > 20 and i == 0:
    #         print(
    #             f"{temp[-1]}. 20 degree found first itself. checking next batch for lowest degree"
    #         )
    #         degree = temp[-1]
    #         temp1 = results[(i + 1) * split : split * (i + 2) :]
    #         # print(temp1)
    #         degree1 = min(temp1)
    #         if degree1 < degree:
    #             degree = degree1
    #         else:
    #             print(f"no degree found lower than {degree}")
    #         break
    #     else:
    #         print("20 degree found.")
    #         temp1 = [i for i in temp1 if int(i) <= 20]
    #         # print(temp)
    #         degree = [i for i in temp if int(i) <= 20]
    #         if degree:
    #             degree = max(degree)
    #         elif i == 0:
    #             degree = results[-1]
    #         else:
    #             degree = max(temp1)
    #         break
    # if degree == 0:
    #     degree = max(results)
    print("Selected", degree)

    point = get_next_waypoint(point, 7)
    next_point = get_next_waypoint(point, 7)
    prev_point = get_prev_waypoint(point, 7)
    # print("(", prev_point, ")", point, next_point)
    a = track_data[point]
    b = track_data[next_point]
    c = track_data[prev_point]
    angle1 = get_angle_between_coordinates(a, b)
    angle2 = get_angle_between_coordinates(a, c)
    result = get_direction_diff(angle1, angle2)
    direction = "far"
    if int(result) <= 100:
        direction = "immediate"

    # print(f"{a},{b} vs {a},{c} : {angle1} vs {angle2}")
    print(
        "(",
        prev_point,
        ")",
        point,
        next_point,
        "upcoming uturn",
        result,
        direction,
        "\n",
    )

    # break
