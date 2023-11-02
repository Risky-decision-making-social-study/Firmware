"""[summary]
Sampling [_risk/_safe and _human/_machine]
Objective: monkey experiences the consequences of pulling the risky/safe lever

Number of apparatuses mounted: 1 (experimenter will alternate which cage is used)

Session number: 4 x sessions per lever type (i.e. in total each monkey experiences 8 sampling sessions) with a max. of 2 sessions per day (one in the morning and one in the afternoon testing slot)

Counterbalancing: Each monkey receives a block of 4 risky lever sessions and a block of 4 safe lever sessions with the appropriate distributor (the distributor that they will experience in the subsequent test condition).

No criterion needs to be passed to move from this session type

Event sequence:
    1. Box lights up in “risky”/”safe” colour
    2. After 5 s red lever light on apparatus is turned on (for max.10 s)
    3. Monkey pulls lever, an acoustic cue sounds and at the same time both lights (lever and box) go out
    4. Experimenter/machine distributes reward
    5. 5 s inter-trial interval gives monkey time to consume food
    6. If monkey does not pull the lever within the 10 s, the light goes out and there is a 10 s inter-trial interval.
    7. If monkey pulls lever, repeat sequence 1-4 another 15 times

Notes on randomisation:
    + The side where the apparatus is mounted will be pseudo-randomised. Each lever type should be presented two times per side.
    + When it comes to the risky lever, we would like to change how the carousel reward deployment works. Ideally we would bait the risky carousel compartments 1-8 with 7 reward items and compartments 9-16 with 1 reward item and the program selects the appropriate compartment to deploy according to the unique pseudo-randomisation scheme of the session. This minimises the opportunity for experimenter error. Note that within a test session, a maximum of four jackpots (7-item rewards) and four losses (1-item rewards) can be dispensed consecutively.

The program should log:
    + Pull-latency (time between the red-light coming on and a lever being pulled)
    + Duration, timestamp and frequency of lever touches
    + Whether a timeout occurred

"""

import logging
import os
import signal
import sys
import time
from datetime import datetime, timedelta

import setup_client_logging
from apparatus import util
from apparatus.client import ApparatusClient
from apparatus.csv_writer import CSVWriter
from apparatus.kbhit import KBHit
from apparatus.ledout import COLORS  # Color definitions
from monkey_list import MONKEYS, getMonkeyDBVariables

# CONFIG ##################################################


# Session #juditchangeme ==================================

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
) = getMonkeyDBVariables(MONKEYS["DUMMY"])
CONDITION = "quantity"
SESSION_TYPE = "sampling_session"
APPARATUS_USED = "RIGHT"
SESSION_NR = 1


# Depends on SAMPLING_SESSION TYPE
# --- False => human distributor, True => machine distributor
DISTRIBUTOR_MACHINE = True
# --- False => safe lever, True => risk lever
RISK_LEVER = False

# Reward settings
WIN_REWARD_OUTCOME = 7  # Winning reward outcome
LOS_REWARD_OUTCOME = 1  # Losing reward outcome
SAF_REWARD_OUTCOME = 4  # Safe reward outcome
NON_REWARD_OUTCOME = "None"  # Timeout reward outcome
RISK_BAIT_PATTERN = [
    WIN_REWARD_OUTCOME,  # 1
    WIN_REWARD_OUTCOME,  # 2
    WIN_REWARD_OUTCOME,  # 3
    WIN_REWARD_OUTCOME,  # 4
    WIN_REWARD_OUTCOME,  # 5
    WIN_REWARD_OUTCOME,  # 6
    WIN_REWARD_OUTCOME,  # 7
    WIN_REWARD_OUTCOME,  # 8
    LOS_REWARD_OUTCOME,  # 9
    LOS_REWARD_OUTCOME,  # 10
    LOS_REWARD_OUTCOME,  # 11
    LOS_REWARD_OUTCOME,  # 12
    LOS_REWARD_OUTCOME,  # 13
    LOS_REWARD_OUTCOME,  # 14
    LOS_REWARD_OUTCOME,  # 15
    LOS_REWARD_OUTCOME,  # 16
]
SAFE_BAIT_PATTERN = [
    SAF_REWARD_OUTCOME,  # 1
    SAF_REWARD_OUTCOME,  # 2
    SAF_REWARD_OUTCOME,  # 3
    SAF_REWARD_OUTCOME,  # 4
    SAF_REWARD_OUTCOME,  # 5
    SAF_REWARD_OUTCOME,  # 6
    SAF_REWARD_OUTCOME,  # 7
    SAF_REWARD_OUTCOME,  # 8
    SAF_REWARD_OUTCOME,  # 9
    SAF_REWARD_OUTCOME,  # 10
    SAF_REWARD_OUTCOME,  # 11
    SAF_REWARD_OUTCOME,  # 12
    SAF_REWARD_OUTCOME,  # 13
    SAF_REWARD_OUTCOME,  # 14
    SAF_REWARD_OUTCOME,  # 15
    SAF_REWARD_OUTCOME,  # 16
]

HUMANLIGHT_COLORCODE = {
    LOS_REWARD_OUTCOME: COLORS['RED'],
    SAF_REWARD_OUTCOME: COLORS['YELLOW'],
    WIN_REWARD_OUTCOME: COLORS['GREEN'],
}

# Session #juditchangeme ==================================

# Auto settings
DISTRIBUTOR = "MACHINE" if DISTRIBUTOR_MACHINE else "HUMAN"

# Random lose/win for food deployment
PSEUDO_RANDOM_RISK_OUTCOME = [
    LOS_REWARD_OUTCOME if i else WIN_REWARD_OUTCOME for i in util.apparatus_pseudo_random_generator(16)]

# sampling session type determination
if RISK_LEVER:
    SESSION_TYPE += "-risk_lever"
else:
    SESSION_TYPE += "-safe_lever"

if DISTRIBUTOR_MACHINE:
    SESSION_TYPE += "-machine_distributor"
else:
    SESSION_TYPE += "-human_distributor"


# |- PRETRIAL_LIGHT_TIME -|- LEVER_ACTIVE_TIME -|- INTER_TRIAL -------|
# -- INTER_TRIAL_DELAY ---|---------------------|- INTER_TRIAL_DELAY --
LEVER_ACTIVE_TIME = 20
PRETRIAL_LIGHT_TIME = 20
INTER_TRIAL_DELAY = 30  # containing PRETRIAL_LIGHT_TIME


# Apparatus
VOLUME = 90
TEST_LIGHT_COLOR = COLORS['RED']
HUMAN_LIGHT_COLOR = COLORS['RED']
APPARATUS_COLOR = COLOR_RISK if RISK_LEVER else COLOR_SAFE
APPARATUS_COLORS = [APPARATUS_COLOR]
HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server
DEBUGLEVEL = logging.INFO
# DEBUGLEVEL = logging.DEBUG
SYCHRONISATION_DELAY = 1
DEPLOY_DELAY = 2
if APPARATUS_USED == "LEFT":
    HOST = HOST_LEFT
elif APPARATUS_USED == "RIGHT":
    HOST = HOST_RIGHT
else:
    logging.error("Config Error")
    sys.exit(1)


if INTER_TRIAL_DELAY - PRETRIAL_LIGHT_TIME - SYCHRONISATION_DELAY - DEPLOY_DELAY < 0:
    logging.error(
        "INTER_TRIAL_DELAY timing is to short and will cause timing issues!")

# SETUP ###################################################
setup_client_logging.setup(os.path.basename(__file__)[:-3], DEBUGLEVEL)


logging.info(
    "Welcome!\n" +
    "Press SPACE to pause next trial\n" +
    "Press ESC to stop after current trial\n"+"---")

util.log_rand_info("PSEUDO_RANDOM_RISK_OUTCOME",
                   PSEUDO_RANDOM_RISK_OUTCOME)

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


def csv_event_callback(event_id, event_state, timestamp=None):
    logging.debug("CSV EVENT %s, %s" % (event_id, event_state,))
    csv_logger.write(
        trial_nr=trial_id+1,
        event_side=APPARATUS_USED,
        event_id=event_id,
        event_state=event_state,
        timestamp=timestamp
    )


# Connect to Apparatus(se)
apparatus = ApparatusClient(
    HOST,
    PORT,
    csv_event_callback,
    csv_event_callback,
    csv_event_callback
)

apparatus.init_hw()


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
    apparatus.close_connection()
    logging.info("CSV Shutdown")
    csv_logger.close()
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
session_log_warnings = False
# --- Set color
apparatus.set_light(COLORS['BLACK'])
apparatus.set_test_light(False, TEST_LIGHT_COLOR)
time.sleep(5)


# --- Move to prepare
# safe
apparatus.move_to(apparatus.CAROUSEL_1, util.pop_deploy(
    SAFE_BAIT_PATTERN, SAF_REWARD_OUTCOME, write=False),
    monkey=DISTRIBUTOR_MACHINE, blocking=False)
# risk
apparatus.move_to(apparatus.CAROUSEL_2, util.pop_deploy(
    RISK_BAIT_PATTERN, PSEUDO_RANDOM_RISK_OUTCOME[0], write=False),
    monkey=DISTRIBUTOR_MACHINE, blocking=False)

# start trials
for trial_id in range(0, 16):
    # Pause on p
    pause_on_p()
    # Prepare trial
    apparatus.set_human_light(False, HUMAN_LIGHT_COLOR)
    # --- Wait for the Hardware to reach targets
    apparatus.move_to_wait(apparatus.CAROUSEL_1)
    apparatus.move_to_wait(apparatus.CAROUSEL_2)

    # Trial
    logging.info("Begin Trial No. "+str(trial_id+1))
    csv_logger.write(trial_nr=trial_id+1,
                     event_id="BEGIN_TRIAL")

    # 1. Apparatus lights up in "risky"/"safe" colour (box light)
    apparatus.set_light(APPARATUS_COLOR)

    # Start interface output
    timestamp = datetime.now()+timedelta(seconds=SYCHRONISATION_DELAY)
    timestamp += timedelta(seconds=max(PRETRIAL_LIGHT_TIME -
                           SYCHRONISATION_DELAY, 0))

    apparatus.set_test_light(True, timestamp=timestamp)
    apparatus.set_lever_open(True, timestamp=timestamp)
    apparatus.play_sound("on-status.mp3",
                         volume=VOLUME,
                         timestamp=timestamp)
    util.wait_till(timestamp)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_OPEN",
                     event_side=APPARATUS_USED,
                     event_state=True)
    csv_logger.write(trial_nr=trial_id+1,
                     event_side=APPARATUS_USED,
                     event_id="TEST_LIGHT",
                     event_state=True)

    start = time.time()
    # --- 2. After 5 s red lever light on apparatus is turned on (for max. LEVER_ACTIVE_TIME s)
    lever_pulled = apparatus.wait_lever_state(
        apparatus.LEVER_PULLED, False, LEVER_ACTIVE_TIME)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_OPEN",
                     event_side=APPARATUS_USED,
                     event_state=False)
    apparatus.set_lever_open(False)
    end = time.time()

    logging.info("lever_pulled: "+str(lever_pulled) +
                 " after: "+str(end - start))

    time_to_release = max(0, LEVER_ACTIVE_TIME - (end - start))
    lever_released = apparatus.wait_lever_state(
        apparatus.LEVER_RELEASED, False, time_to_release)
    end = time.time()
    logging.info("lever_released: "+str(lever_released) +
                 " after: "+str(end - start))

    reward_outcome = NON_REWARD_OUTCOME
    apparatus_pulled_str = None
    if lever_pulled and lever_released:
        # Deploy reward
        apparatus_pulled = apparatus
        apparatus_pulled_str = APPARATUS_USED
        logging.info("Pull was %s" % (apparatus_pulled_str,))

        # --- 3. Monkey pulls lever, an acoustic cue sounds and at the same time both lights
        # (lever and box) go out
        apparatus_pulled.play_sound("cash-register.mp3", volume=VOLUME)
        # --- 4. Experimenter/machine distributes reward
        if RISK_LEVER:
            # risky
            reward_outcome = PSEUDO_RANDOM_RISK_OUTCOME[trial_id]
            carousel = apparatus_pulled.CAROUSEL_2
            compartment = util.pop_deploy(
                RISK_BAIT_PATTERN, reward_outcome, write=True)
        else:
            # safe
            reward_outcome = SAF_REWARD_OUTCOME
            carousel = apparatus_pulled.CAROUSEL_1
            compartment = util.pop_deploy(
                SAFE_BAIT_PATTERN, reward_outcome, write=True)
        apparatus_pulled.deploy(carousel, compartment,
                                monkey=DISTRIBUTOR_MACHINE, blocking=False)

        # --- signal human
        apparatus_pulled.set_human_light(
            True, HUMANLIGHT_COLORCODE[reward_outcome])

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
                     event_side=apparatus_pulled_str,
                     event_state=False)
    apparatus.set_test_light(False)
    apparatus.set_light(COLORS['BLACK'])

    # Warn experimenter
    session_log_pull.append(lever_pulled)
    session_log_warnings = session_log_warnings or not util.check_log(
        session_log_pull)

    # Wait indefinitely until the lever is up
    logging.info("Wait indefinitely until the lever is up")
    apparatus.wait_lever_state(
        apparatus.LEVER_RELEASED, False)

    # --- Move to prepare next trial
    time.sleep(DEPLOY_DELAY)
    if trial_id < 15:
        # safe
        apparatus.move_to(apparatus.CAROUSEL_1, util.pop_deploy(
            SAFE_BAIT_PATTERN, SAF_REWARD_OUTCOME, write=False),
            monkey=DISTRIBUTOR_MACHINE, blocking=False)
        # risk
        apparatus.move_to(apparatus.CAROUSEL_2, util.pop_deploy(
            RISK_BAIT_PATTERN, PSEUDO_RANDOM_RISK_OUTCOME[trial_id + 1], write=False),
            monkey=DISTRIBUTOR_MACHINE, blocking=False)

    logging.info("Starting inter-trial interval")
    if not lever_pulled:
        # 6. If monkey does not pull the lever within the 10 s, the
        # light goes out and there is a 5 s inter-trial interval.
        # => no penalty time
        time.sleep(0)
    # 5. 5 s inter-trial interval gives monkey time to consume food
    time.sleep(INTER_TRIAL_DELAY-PRETRIAL_LIGHT_TIME-DEPLOY_DELAY)
    # 7. If monkey pulls lever, repeat sequence 1-4 another 15 times

# Cleanup
apparatus.empty_human()
apparatus.move_to(apparatus.CAROUSEL_1,
                  0,
                  monkey=DISTRIBUTOR_MACHINE,
                  blocking=False)
apparatus.move_to(apparatus.CAROUSEL_2,
                  0,
                  monkey=DISTRIBUTOR_MACHINE,
                  blocking=False)
apparatus.move_to_wait(apparatus.CAROUSEL_1)
apparatus.move_to_wait(apparatus.CAROUSEL_2)
apparatus.set_light(COLORS['BLACK'])

if session_log_warnings:
    logging.warn("There are SESSION WARNINGS in the log!")

session_valid = ask_session_valid()

exit_handler()
