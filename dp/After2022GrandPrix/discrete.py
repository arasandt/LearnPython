max_speed = 4
min_speed = 1.3
max_steer = 30  # left steer
min_steer = -20  # right steer
slots = 15

all_speeds = []
speed_step = (max_speed - min_speed) / slots
print(speed_step)
speed_step *= 1 - abs(min_steer / max_steer) / 4
print(speed_step)
current_speed = min_speed
while current_speed <= max_speed:
    all_speeds.append(round(current_speed, 2))
    current_speed += speed_step
# all_speeds = all_speeds[:slots]
print(all_speeds)
print(len(all_speeds))

all_steers = []
steer_factor = abs(min_steer / max_steer)
# steer_step = max_steer / slots
# steer_step += steer_factor
# print(steer_step)
# print(steer_factor)
# 0 / 0
# steer_step = (max_steer - min_steer) * steer_factor / (slots * 0.5)
steer_step = max_steer / (len(all_speeds) - 1)
current_steer = 0
while current_steer <= max_steer:
    all_steers.append(round(current_steer, 2))
    current_steer += steer_step
# all_steers = all_steers[:slots]
print(all_steers)
print(len(all_steers))

space = []
for i, speed in enumerate(all_speeds[::-1]):
    if i == 0:
        space.append(
            {
                "steering_angle": 0,
                "speed": speed,
            }
        )
    else:
        try:
            steer_index = all_steers.index(0) + i
            space.append(
                {
                    "steering_angle": all_steers[steer_index],
                    "speed": speed,
                }
            )
            if -all_steers[steer_index] >= min_steer:
                space.append(
                    {
                        "steering_angle": -all_steers[steer_index],
                        "speed": speed,
                    }
                )
        except IndexError as error:
            print(error)
            break

print(space)
print(len(space))
