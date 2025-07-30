from datetime import datetime, timedelta

from training.constans import TIME_REGISTER_TRAINING, TIMERS_REGISTER_TRAINING, TIME_TRAINING


def get_near_end_time_training() -> tuple[int, bool]:
    now = datetime.now()
    nearest_time = None
    is_in_training_zone = False
    for time_str in TIMERS_REGISTER_TRAINING:
        training_time = datetime.strptime(time_str, "%H:%M").replace(year=now.year, month=now.month, day=now.day)
        end_time_training = training_time + TIME_REGISTER_TRAINING + TIME_TRAINING
        if end_time_training < now:
            end_time_training += timedelta(days=1)
        if nearest_time is None or end_time_training < nearest_time:
            nearest_time = end_time_training
        if training_time <= now <= end_time_training:
            is_in_training_zone = True
    return int(nearest_time.timestamp()), is_in_training_zone