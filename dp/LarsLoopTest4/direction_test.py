MAX_STEERING = 30


def get_turn_direction(immediate_direction, lookahead_direction, heading):
    if immediate_direction < 0:
        immediate_direction += 360
    if lookahead_direction < 0:
        lookahead_direction += 360
    if heading < 0:
        heading += 360

    if abs(immediate_direction - lookahead_direction) <= MAX_STEERING * 3:
        if lookahead_direction > immediate_direction:
            direction = "left"
        else:
            direction = "right"
    elif 360 - abs(immediate_direction - lookahead_direction) <= MAX_STEERING * 3:
        if lookahead_direction > immediate_direction:
            direction = "right"
        else:
            direction = "left"
    else:
        direction = 0
    return direction, immediate_direction, lookahead_direction, heading


def direction_reward_fn(immediate_direction, lookahead_direction, heading):
    direction_reward = 1

    (
        turn_direction,
        new_immediate_direction,
        new_lookahead_direction,
        new_heading,
    ) = get_turn_direction(immediate_direction, lookahead_direction, heading)
    if not turn_direction:
        return 0, 0

    if (
        new_immediate_direction <= new_heading <= new_lookahead_direction
    ) and turn_direction == "left":
        pass
    elif (
        new_immediate_direction >= new_heading >= new_lookahead_direction
    ) and turn_direction == "right":
        pass
    elif (
        immediate_direction >= heading >= lookahead_direction
    ) and turn_direction == "right":
        pass
    elif (
        immediate_direction <= heading <= lookahead_direction
    ) and turn_direction == "left":
        pass
    else:
        direction_reward = 0.15

    return direction_reward, turn_direction


# immediate_direction, lookahead_direction, heading = 30, 60, 40
# immediate_direction, lookahead_direction, heading = 160, -160, 175
# immediate_direction, lookahead_direction, heading = 160, -160, -175
# immediate_direction, lookahead_direction, heading = -60, -30, -40
# immediate_direction, lookahead_direction, heading = -20, 10, 1
# immediate_direction, lookahead_direction, heading = -20, 10, -1

# immediate_direction, lookahead_direction, heading = 60, 30, 40
# immediate_direction, lookahead_direction, heading = -160, 160, 175
# immediate_direction, lookahead_direction, heading = -160, 160, -175
# immediate_direction, lookahead_direction, heading = -30, -60, -40
# immediate_direction, lookahead_direction, heading = 20, -10, 1
# immediate_direction, lookahead_direction, heading = 20, -10, -1


print(direction_reward_fn(immediate_direction, lookahead_direction, heading))
