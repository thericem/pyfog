import numpy as np

def square_pulse(points,
                 duty_cycle=.5,
                 rise_time_over_cycle_time=0,
                 fall_time_over_cycle_time=0):
    """Note:
    this whole calculation in this function runs in O(N) time.
    TODO:
    This algorithm could likely be improved, though not priority
    """

    # xor
    #if bool(rise_time_over_cycle_time) != bool(fall_time_over_cycle_time):
     #   rise_time_over_cycle_time = fall_time_over_cycle_time = max(
     #       rise_time_over_cycle_time, fall_time_over_cycle_time)

    time = np.linspace(0, 1, points, endpoint=False)

    def get_height_at_progress(ratio):
        if ratio == 0:
            return .5 if rise_time_over_cycle_time else 1
        elif ratio == duty_cycle:
            return .5 if fall_time_over_cycle_time else 0
        elif ratio > 0 and ratio <= rise_time_over_cycle_time / 2:
            return ratio / rise_time_over_cycle_time + .5
        elif ratio > rise_time_over_cycle_time / 2 and ratio <= duty_cycle - \
                        fall_time_over_cycle_time / 2:
            return 1
        elif ratio > duty_cycle - fall_time_over_cycle_time / 2 and ratio <= \
                        duty_cycle + fall_time_over_cycle_time / 2:
            return 1 - (
                       ratio - duty_cycle + fall_time_over_cycle_time / 2) / \
                       fall_time_over_cycle_time
        elif ratio > duty_cycle + fall_time_over_cycle_time / 2 and ratio <= \
                        1 - rise_time_over_cycle_time / 2:
            return 0
        else:
            return (
                   ratio - 1 + rise_time_over_cycle_time / 2) / rise_time_over_cycle_time

    def normalize(ratio):
        v = 2 * get_height_at_progress(ratio) - 1
        if v > 1: return 1
        if v < -1: return -1
        return v

    return np.array([normalize(t)
                    for t in time])