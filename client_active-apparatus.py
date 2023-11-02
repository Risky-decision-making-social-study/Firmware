"""[summary]
Active apparatus (_human/_machine)
Objective: monkey consolidates and demonstrates what it has learned about the red light-lever association

Session number: no set session number, but there is a criterion which each monkey must pass (see below)

Number of apparatuses mounted: 2, the monkey roams between the LH and the RH cages

Criterion to move on from active apparatus sessions: monkey is above chance in pulling the “right” lever in 2 consecutive sessions on 2 different test days. In case the monkey has not reached criterion after 36 sessions, then s/he must select the “right” lever in 12/16 trials in 3 consecutive sessions on 3 different test days

Event sequence:
    1. The two apparatuses are not coupled – the red lever light on one of the apparatuses turns on (for max. 10 s); on which apparatus the red lever light lights up is pseudo-randomised (the same apparatus should not light up more than three four times in a row).
    2. Monkey pulls a lever - an acoustic cue sounds and at the same time the red lever light goes out
    3. Experimenter/machine hands out reward (whether experimenter/machine depends on the test condition the monkey will receive first i.e. if a monkey is to experience the human distributor test condition first, then the monkey receives the active_apparatus_human sessions)
    4. 10 s inter-trial interval gives monkey time to consume food
    5. If monkey does not pull the lever within the 10 s, the red lever light goes out and there is a 10 s inter-trial interval.
    6. If monkey pulls a lever, repeat event sequence 1 to 4 another 15 times

The experimenter will keep track of whether the monkey has reached criterion and can move on to the next session type.

Notes on randomisation
    + The side where the red lever light comes on is pseudo-randomised for each individual; we randomise which side lights during the 16 trials but no side may light up more than four consecutive times in a row and each side should light up an equal number of times (8 times).

The program should log:
    + How many active_apparatus sessions the individual experienced
    + Which lever was finally pulled in each trial (the “correct” or the “wrong” lever); the correct lever being the one attached to the apparatus where the red lever light was on.
    + Duration and frequency of lever touches associated with both levers
    + Pull-latency (time between the red lever light coming on and a lever being pulled)

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
from monkey_list import MONKEYS, getMonkeyDBVariables

# CONFIG ##################################################

# Session #juditchangeme
# Monkey Picker
(
    SUBJECT_NAME,
    SEX,
    AGE,
    COLOR_RISK,
    COLOR_SAFE,
    DISTRIBUTOR_FIRST,
    CONTROLLER_ID,
    DISTRIBUTOR_ID,
) = getMonkeyDBVariables(MONKEYS["MEIWI"])
CONDITION = "quantity"
SESSION_TYPE = "active_apparatus"
APPARATUS_USED = "BOTH"
SESSION_NR = 29


# DISTRIBUTOR True => Machine, False => Human
DISTRIBUTOR_MACHINE = False

# Reward settings
CUR_REWARD_OUTCOME = 2  # Current reward outcome
NON_REWARD_OUTCOME = "None"  # Timeout reward outcome

# Session #juditchangeme ==================================

# Auto settings
DISTRIBUTOR = "MACHINE" if DISTRIBUTOR_MACHINE else "HUMAN"

# 1. (1/2) The two apparatuses are not coupled – the red lever light on one
# of the apparatuses turns on (for max. 10 s); on which apparatus
# the red lever light lights up is pseudo-randomised (the same
# apparatus should not light up more than four times in a row).

PSEUDO_RANDOM_APPARATUS = util.apparatus_pseudo_random_generator(16)

PSEUDO_RANDOM_APPARATUS_STR = [
    "LEFT" if a else "RIGHT" for a in PSEUDO_RANDOM_APPARATUS]

PSEUDO_RANDOM_COLORS = util.apparatus_pseudo_random_generator(16)

# |- LEVER_ACTIVE_TIME -|- INTER_TRIAL_DELAY -|
LEVER_ACTIVE_TIME = 20
INTER_TRIAL_DELAY = 10

# Apparatus
VOLUME = 90
TEST_LIGHT_COLOR = COLORS['RED']
HUMAN_LIGHT_COLOR = COLORS['RED']
APPARATUS_COLOR_LEFT = COLORS['BLACK']  # Off
APPARATUS_COLOR_RIGHT = COLORS['BLACK']  # Off
APPARATUS_COLORS = [COLORS['BLACK'], COLORS['BLACK']]  # Off
HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server
DEBUGLEVEL = logging.INFO
# DEBUGLEVEL = logging.DEBUG
SYCHRONISATION_DELAY = 1

# SETUP ###################################################
setup_client_logging.setup(os.path.basename(__file__)[:-3], DEBUGLEVEL)

logging.info(
    "Welcome!\n" +
    "Press SPACE to pause next trial\n" +
    "Press ESC to stop after current trial\n"+"---")

util.log_rand_info("PSEUDO_RANDOM_APPARATUS", PSEUDO_RANDOM_APPARATUS)
util.log_rand_info("PSEUDO_RANDOM_COLORS", PSEUDO_RANDOM_COLORS)

csv_logger = CSVWriter(
    './data_raw_csv',
    controller_id=CONTROLLER_ID,
    distributor_id=DISTRIBUTOR_ID,
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
            input("Paused! Press enter to continue...\n")


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
                     event_id="BEGIN_TRIAL")

    # randomly select trial apparatus and color
    apparatus_trial = apparatus_left if PSEUDO_RANDOM_APPARATUS[trial_id] else apparatus_right
    apparatus_trial.set_light(APPARATUS_COLORS[PSEUDO_RANDOM_COLORS[trial_id]])

    # Start interface output
    timestamp = datetime.now()+timedelta(seconds=SYCHRONISATION_DELAY)

    apparatus_trial.set_test_light(True, timestamp=timestamp)
    apparatus_trial.set_lever_open(True, timestamp=timestamp)
    apparatus_trial.play_sound("on-status.mp3",
                               volume=VOLUME,
                               timestamp=timestamp)
    util.wait_till(timestamp)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_OPEN",
                     event_side=PSEUDO_RANDOM_APPARATUS_STR[trial_id],
                     event_state=True)
    csv_logger.write(trial_nr=trial_id+1,
                     event_side=PSEUDO_RANDOM_APPARATUS_STR[trial_id],
                     event_id="TEST_LIGHT",
                     event_state=True)

    start = time.time()
    # 1. (2/2) The two apparatuses are not coupled – the red lever light on one
    # of the apparatuses turns on (for max. LEVER_ACTIVE_TIME s) [...]
    lever_pulled = apparatus_trial.wait_lever_state(
        apparatus_left.LEVER_PULLED, False, LEVER_ACTIVE_TIME)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="TEST_LIGHT",
                     event_side=PSEUDO_RANDOM_APPARATUS_STR[trial_id],
                     event_state=False)
    apparatus_trial.set_lever_open(False)
    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_OPEN",
                     event_side=PSEUDO_RANDOM_APPARATUS_STR[trial_id],
                     event_state=False)
    end = time.time()

    logging.info("lever_pulled: "+str(lever_pulled) +
                 " after: "+str(end - start))

    time_to_release = max(0, LEVER_ACTIVE_TIME - (end - start))
    lever_released = apparatus_trial.wait_lever_state(
        apparatus_trial.LEVER_RELEASED, False, time_to_release)
    end = time.time()
    logging.info("lever_released: "+str(lever_released) +
                 " after: "+str(end - start))

    reward_outcome = NON_REWARD_OUTCOME
    apparatus_pulled_str = None
    if lever_pulled and lever_released:
        # Deploy reward
        # --- determine side that was pulled
        apparatus_pulled = apparatus_trial
        apparatus_pulled_str = PSEUDO_RANDOM_APPARATUS_STR[trial_id]
        session_log_side.append(apparatus_pulled_str)
        logging.info("Pull was %s" % (apparatus_pulled_str,))

        # --- signal human
        apparatus_pulled.set_human_light(True)
        # --- 2. Monkey pulls a lever - an acoustic cue sounds and at the same
        # time the red lever light goes out
        apparatus_pulled.play_sound("cash-register.mp3", volume=VOLUME)
        # --- 3. Experimenter/machine hands out reward (whether
        # experimenter/machine depends on the test condition the monkey will
        # receive first i.e. if a monkey is to experience the human distributor
        # test condition first, then the monkey receives the
        # active_apparatus_human sessions)
        apparatus_pulled.deploy(apparatus_pulled.CAROUSEL_1, trial_id,
                                monkey=DISTRIBUTOR_MACHINE, blocking=False)
        reward_outcome = CUR_REWARD_OUTCOME

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_PULLED",
                     event_side=apparatus_pulled_str,
                     event_state=lever_pulled and lever_released)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="REWARD_OUTCOME",
                     event_side=apparatus_pulled_str,
                     event_state=reward_outcome)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="TEST_LIGHT",
                     event_side=PSEUDO_RANDOM_APPARATUS_STR[trial_id],
                     event_state=False)
    apparatus_trial.set_test_light(False)
    apparatus_trial.set_light(COLORS['BLACK'])

    # Warn experimenter
    if not lever_pulled:
        session_log_side.append("NONE")
    session_log_pull.append(lever_pulled)
    session_log_warnings = session_log_warnings or not util.check_log(
        session_log_pull)

    # Wait indefinitely until the lever is up
    logging.info("Wait indefinitely until the lever is up")
    apparatus_trial.wait_lever_state(
        apparatus_trial.LEVER_RELEASED, False)

    logging.info("Starting inter-trial interval")
    if not lever_pulled:
        # --- 5. If monkey does not pull the lever within the LEVER_ACTIVE_TIME s, the red
        # lever light goes out and there is a INTER_TRIAL_DELAY s inter-trial interval.
        # => no penalty time
        time.sleep(0)
    # --- 4. INTER_TRIAL_DELAY s inter-trial interval gives monkey time to consume food
    time.sleep(INTER_TRIAL_DELAY-SYCHRONISATION_DELAY)

    # 6. If monkey pulls a lever, repeat event sequence 1 to 4 another 15 times

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
