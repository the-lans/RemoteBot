import threading
import time
from schedule import every, repeat, run_pending

from backend_server.config import main_conf
from backend_server import root_connect, tracking_files, file_tracking
from backend_server.users import current_user


def run_continuously(interval=1):
    """Continuously run, while executing pending jobs at each
    elapsed time interval.
    @return cease_continuous_run: threading. Event which can
    be set to cease continuous run. Please note that it is
    *intended behavior that run_continuously() does not run
    missed jobs*. For example, if you've registered a job that
    should run every minute and you set a continuous run
    interval of one hour then your job won't be run 60 times
    at each interval but only once.
    """
    cease_continuous_run = threading.Event()

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while not cease_continuous_run.is_set():
                run_pending()
                time.sleep(interval)

    continuous_thread = ScheduleThread()
    continuous_thread.start()
    return cease_continuous_run


@repeat(every(10).minutes)
def task_file_tracking():
    """Tasks: check file tracking"""
    if main_conf['tasks']:
        file_tracking(tracking_files, current_user, root_connect)
