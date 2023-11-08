"""[summary]
Test script to verify light-on and sound timing works and is not distraction for the subjects
"""
import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta

import setup_client_logging
from apparatus import event_util, util
from apparatus.client import ApparatusClient
from apparatus.csv_writer import CSVWriter
from apparatus.kbhit import KBHit
from apparatus.ledout import COLORS  # Color definitions

# CONFIG ##################################################

# Session settings #changeme ==================================
EXPERIMENTER = "Louis"
SUBJECT_NAME = "Balu"
SEX = "M"
AGE = 123
COLOR_RISK = "BLUE"
CONDITION = "NA"
DISTRIBUTOR_FIRST = "HUMAN"
SESSION_TYPE = "timing_test"
APPARATUS_USED = "BOTH"
SESSION_NR = 1

# Depends on DISTRIBUTOR_FIRST
DISTRIBUTOR_MACHINE = True
# Session settings #changeme ==================================

# Auto settings
COLOR_SAFE = "WHITE" if COLOR_RISK == "BLUE" else "BLUE"
DISTRIBUTOR = "MACHINE" if DISTRIBUTOR_MACHINE else "HUMAN"

# Apparatus
VOLUME = 90
TEST_LIGHT_COLOR = COLORS['RED']
HUMAN_LIGHT_COLOR = COLORS['RED']
SIDE_RISKY = "LEFT"
APPARATUS_COLOR_LEFT = COLOR_RISK
APPARATUS_COLOR_RIGHT = COLOR_SAFE
APPARATUS_COLORS = [APPARATUS_COLOR_LEFT, APPARATUS_COLOR_RIGHT]
HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server
DEBUGLEVEL = logging.INFO
# DEBUGLEVEL = logging.DEBUG
SYCHRONISATION_DELAY = 2

# SETUP ###################################################
setup_client_logging.setup(os.path.basename(__file__)[:-3], DEBUGLEVEL)


csv_logger = CSVWriter(
    './data_raw_csv',
    experimenter=EXPERIMENTER,
    subject_name=SUBJECT_NAME,
    sex=SEX,
    age=AGE,
    condition=CONDITION,
    color_risk=COLOR_RISK,
    color_safe=COLOR_SAFE,
    distributor_first=DISTRIBUTOR_FIRST,
    distributor=DISTRIBUTOR,
    session_type=SESSION_TYPE,
    session_nr=SESSION_NR
)
csv_logger.write_header()
csv_logger.write(event_id="SESSION_START")

trial_id = -1


def csv_event_callback(event_id, event_state, timestamp=None, event_side=None):
    logging.debug("CSV EVENT %s, %s" % (event_id, event_state,))
    csv_logger.write(
        trial_nr=trial_id+1,
        event_side=event_side,
        side_risky=SIDE_RISKY,
        event_id=event_id,
        event_state=event_state,
        timestamp=timestamp
    )


def csv_event_callback_left(event_id, event_state, timestamp=None): return csv_event_callback(
    event_id, event_state, timestamp, "LEFT"),


def csv_event_callback_right(event_id, event_state, timestamp=None): return csv_event_callback(
    event_id, event_state, timestamp, "RIGHT")


# Connect to Apparatus(se)
apparatus_left = ApparatusClient(
    HOST_LEFT,
    PORT,
    csv_event_callback_left,
    csv_event_callback_left,
    csv_event_callback_left
)
apparatus_left.init_hw()

apparatus_right = ApparatusClient(
    HOST_RIGHT,
    PORT,
    csv_event_callback_right,
    csv_event_callback_right,
    csv_event_callback_right
)
apparatus_right.init_hw()


session_valid = False


def ask_session_valid(question="Is the session valid?"):
    while True:  # "the answer is invalid"
        reply = str(input(question+' (Y/n): ')).lower().strip()
        print(reply+"\n")
        if len(reply) == 0 or reply[0].lower() == 'y':
            return True
        if reply[0].lower() == 'n':
            return False


# Cleanup handler
def exit_handler(signum=None, frame=None):
    csv_logger.write(event_id="SESSION_VALID", event_state=session_valid)
    csv_logger.write(event_id="SESSION_END")
    logging.info("Network Shutdown")
    apparatus_left.close_connection()
    apparatus_right.close_connection()
    logging.info("CSV Shutdown")
    csv_logger.close()
    logging.info("OrThreads join")
    event_util.joinThreads()
    logging.info("He's dead Jim!")
    sys.exit(0)


kb = KBHit()


def pause_on_p():
    if kb.kbhit():
        c = kb.getch()
        if ord(c) == 27:  # ESC
            exit_handler()
        if ord(c) == 32:  # SPACE
            csv_logger.write(event_id="SESSION_FREEZE")
            input("Paused! Press enter to continue...\n")
            csv_logger.write(event_id="SESSION_RESUME")


signal.signal(signal.SIGINT, exit_handler)


# TRIAL CODE ##############################################
logging.info("Start %s" % (SESSION_TYPE,))
# Prepare
session_log_pull = []
session_log_side = []
session_log_warnings = False
# --- Set color
apparatus_left.set_light(APPARATUS_COLOR_LEFT)
apparatus_right.set_light(APPARATUS_COLOR_RIGHT)
apparatus_left.set_test_light(False, TEST_LIGHT_COLOR)
apparatus_right.set_test_light(False, TEST_LIGHT_COLOR)
time.sleep(5)
apparatus_pulled = None

# start trials
for trial_id in range(0, 16):
    # Pause on p
    pause_on_p()
    # Prepare trial
    apparatus_left.set_human_light(False, HUMAN_LIGHT_COLOR)
    apparatus_right.set_human_light(False, HUMAN_LIGHT_COLOR)
    # --- Wait for the Hardware to reach targets
    apparatus_left.move_to_wait(apparatus_left.CAROUSEL_1)
    apparatus_left.move_to_wait(apparatus_left.CAROUSEL_2)
    apparatus_right.move_to_wait(apparatus_right.CAROUSEL_1)
    apparatus_right.move_to_wait(apparatus_right.CAROUSEL_2)
    # --- Move to trial ID
    apparatus_left.move_to(apparatus_left.CAROUSEL_1, trial_id,
                           monkey=DISTRIBUTOR_MACHINE)
    apparatus_left.move_to(apparatus_left.CAROUSEL_2, trial_id,
                           monkey=DISTRIBUTOR_MACHINE, blocking=False)
    apparatus_right.move_to(apparatus_right.CAROUSEL_1, trial_id,
                            monkey=DISTRIBUTOR_MACHINE, blocking=False)
    apparatus_right.move_to(apparatus_right.CAROUSEL_2, trial_id,
                            monkey=DISTRIBUTOR_MACHINE, blocking=False)

    # Trial
    logging.info("Begin Trial No. "+str(trial_id+1))
    csv_logger.write(trial_nr=trial_id+1,
                     side_risky=SIDE_RISKY,

                     event_id="BEGIN_TRIAL")

    # Start interface output
    timestamp = datetime.now()+timedelta(seconds=SYCHRONISATION_DELAY)

    apparatus_left.set_test_light(True, timestamp=timestamp)
    apparatus_right.set_test_light(True, timestamp=timestamp)
    apparatus_left.set_lever_open(True, timestamp=timestamp)
    apparatus_right.set_lever_open(True, timestamp=timestamp)
    apparatus_left.play_sound("on-status.mp3",
                              volume=VOLUME,
                              timestamp=timestamp)
    apparatus_right.play_sound("on-status.mp3",
                               volume=VOLUME,
                               timestamp=timestamp)

    util.wait_till(timestamp)
    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_OPEN",
                     event_side="BOTH",
                     side_risky=SIDE_RISKY,
                     event_state=True)
    csv_logger.write(trial_nr=trial_id+1,
                     event_side="BOTH",
                     side_risky=SIDE_RISKY,
                     event_id="TEST_LIGHT",
                     event_state=True)

    start = time.time()
    # --- 1. Light on apparatus turns on (for max.10 s)
    # --- --- OR WAIT
    event_left = apparatus_left.get_wait_lever_state_event(
        apparatus_left.LEVER_PULLED, False)
    event_right = apparatus_right.get_wait_lever_state_event(
        apparatus_right.LEVER_PULLED, False)
    lever_pulled, finish_event = event_util.OrWait(event_left, event_right, 10)
    # --- --- OR WAIT

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_OPEN",
                     event_side="BOTH",
                     side_risky=SIDE_RISKY,
                     event_state=False)
    apparatus_left.set_lever_open(False)
    apparatus_right.set_lever_open(False)
    end = time.time()

    logging.info("lever_pulled: "+str(lever_pulled) +
                 " after: "+str(end - start))
    apparatus_pulled_str = None
    if lever_pulled:
        # Deploy reward
        # --- determine side that was pulled
        if finish_event == event_left:
            apparatus_pulled = apparatus_left
            apparatus_pulled_str = "LEFT"
        elif finish_event == event_right:
            apparatus_pulled = apparatus_right
            apparatus_pulled_str = "RIGHT"
        session_log_side.append(apparatus_pulled_str)
        logging.info("Pull was %s" % (apparatus_pulled_str,))
        # --- Wait till Lever is pulled and then fully up
        no_fail_release = apparatus_pulled.wait_lever_state(
            apparatus_pulled.LEVER_RELEASED, False, 25)
        logging.info("FAIL_RELEASE %s", not no_fail_release)
        csv_logger.write(
            trial_nr=trial_id+1,
            event_side=apparatus_pulled_str,
            side_risky=SIDE_RISKY,
            event_id="NO_FAIL_RELEASE",
            event_state=no_fail_release,
        )

        if not no_fail_release:
            input("Fail to release! Press any button to continue...")

        # --- signal human
        apparatus_pulled.set_human_light(True)
        # --- 2. Monkey pulls lever, an acoustic cue sounds and at the same time the light
        # goes out
        apparatus_pulled.play_sound("cash-register.mp3", volume=VOLUME)
        # --- 3. Experimenter/Machine distributes reward (which distributor
        # it is depends on the test condition the monkey will receive first)
        apparatus_pulled.deploy(apparatus_pulled.CAROUSEL_1, trial_id,
                                monkey=DISTRIBUTOR_MACHINE, blocking=False)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_PULLED",
                     event_side=apparatus_pulled_str,
                     side_risky=SIDE_RISKY,
                     event_state=lever_pulled)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="TEST_LIGHT",
                     event_side="BOTH",
                     side_risky=SIDE_RISKY,
                     event_state=False)
    apparatus_left.set_test_light(False)
    apparatus_right.set_test_light(False)

    # Warn experimenter
    if not lever_pulled:
        session_log_side.append("NONE")
    session_log_pull.append(lever_pulled)
    session_log_warnings = session_log_warnings or not util.check_log(
        session_log_pull)

    logging.info("Starting inter-trial interval")
    if not lever_pulled:
        # --- alt. 2.-3. If monkey does not pull the lever within the 10 s, the light goes out and there is 15 s inter-trial
        time.sleep(5)
    # --- 4. 10 s inter-trial interval gives monkey time to consume food
    time.sleep(10-SYCHRONISATION_DELAY)

# Cleanup
apparatus_left.empty_human()
apparatus_right.empty_human()
apparatus_left.move_to(apparatus_left.CAROUSEL_1,
                       0,
                       monkey=DISTRIBUTOR_MACHINE,
                       blocking=False)
apparatus_left.move_to(apparatus_left.CAROUSEL_2,
                       0,
                       monkey=DISTRIBUTOR_MACHINE,
                       blocking=False)
apparatus_right.move_to(apparatus_right.CAROUSEL_1,
                        0,
                        monkey=DISTRIBUTOR_MACHINE,
                        blocking=False)
apparatus_right.move_to(apparatus_right.CAROUSEL_2,
                        0,
                        monkey=DISTRIBUTOR_MACHINE,
                        blocking=False)

apparatus_left.move_to_wait(apparatus_left.CAROUSEL_1)
apparatus_right.move_to_wait(apparatus_right.CAROUSEL_1)
apparatus_left.move_to_wait(apparatus_left.CAROUSEL_2)
apparatus_right.move_to_wait(apparatus_right.CAROUSEL_2)

if session_log_warnings:
    logging.warn("There are SESSION WARNINGS in the log!")

session_valid = ask_session_valid()

exit_handler()
