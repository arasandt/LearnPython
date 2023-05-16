import rf

heading = -4
speed = 2
steering = 20
is_left = False
distance_from_center = 28
track_width = 107

lookwayahead_degree, lookahead_degree = 2, 20

reward = rf.Reward(heading, speed, steering, is_left, distance_from_center, track_width)

reward.calc_direction_reward(lookahead_degree)
reward.calc_steering_reward()
reward.calc_speed_reward()
reward.calc_fastlane_reward(lookwayahead_degree)
reward.calc_uturn_reward()

rewards = reward.get_all_rewards(display=True)

print(rewards)
