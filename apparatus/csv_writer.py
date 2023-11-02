import csv
import os
import queue
import threading
from datetime import datetime


class CSVWriter ():
    to_write: queue.Queue
    _thread: threading.Thread

    TIME_FORMAT_FILE = '%Y-%m-%d_%H-%M-%S'
    TIME_FORMAT_LOG = '%Y-%m-%d %H:%M:%S.%f'

    def __init__(self,
                 log_folder_path,
                 controller_id,
                 distributor_id,
                 subject_name,
                 sex,
                 age,
                 condition,
                 color_risk,
                 color_safe,
                 distributor_first,
                 distributor,
                 session_type,
                 session_nr
                 ):

        timestamp = datetime.now().strftime(self.TIME_FORMAT_FILE)
        self.filename = "%s_%s_%s_%s.csv" % (
            timestamp, session_type, session_nr, subject_name)

        self.log_path = os.path.join(log_folder_path, self.filename)

        self.fp = open(self.log_path, 'w', newline='')
        self.csv_writer = csv.writer(self.fp)

        self.static_row = [
            controller_id,
            distributor_id,
            subject_name,
            sex,
            age,
            condition,
            '#%06x' % (color_risk),
            '#%06x' % (color_safe),
            distributor_first,
            distributor,
            session_type,
            session_nr,
        ]

        self.to_write = queue.Queue()
        self._thread = threading.Thread(target=self._bg_thread)
        self._thread.start()

    def _bg_thread(self):
        while True:
            row = self.to_write.get(True)
            if row is None:
                break
            self.csv_writer.writerow(row)
            self.fp.flush()

    def _get_session_CSV(self):
        return ""

    HEAD = [
        "timestamp",
        # Static
        "controller_id",
        "distributor_id",
        "subject_name",
        "sex",
        "age",
        "condition",
        "color_risk",
        "color_safe",
        "distributor_first",
        "distributor",
        "session_type",
        "session_nr",
        # Variable
        "trial_nr",
        "event_side",
        "side_risky",
        "event_id",
        "event_state"
    ]

    def write_header(self):
        self.to_write.put(self.HEAD)

    def write(self,
              trial_nr=0,
              event_side="NA",
              side_risky="NA",
              event_id="No_EVENT",
              event_state="NA",
              timestamp: datetime = None
              ):
        if timestamp is None:
            timestamp = datetime.now()
        if trial_nr is None:
            trial_nr = "NA"
        if event_side is None:
            event_side = "NA"
        if side_risky is None:
            side_risky = "NA"
        if event_id is None:
            event_id = "NA"
        if event_state is None:
            event_state = "NA"

        timestamp_str = timestamp.strftime(self.TIME_FORMAT_LOG)
        self.to_write.put([
            timestamp_str,
            *self.static_row,
            trial_nr,
            event_side,
            side_risky,
            event_id,
            event_state
        ])

    def close(self):
        # TODO parse dict
        self.to_write.put(None)
        # self.to_write.join()
        if self._thread.is_alive():  # TODO necessary?
            self._thread.join()
        self.fp.close()
