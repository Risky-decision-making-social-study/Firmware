"""[summary]
Test condition [_human/_machine]
Objective: monkey faces a choice between the risky and the safe levers

Number of apparatuses mounted: 2, the monkey roams between the LH and the RH cages

Session number: yet to be decided – following meeting on 02.07 have agreed we will run a power analysis in order to establish number of test sessions we should run.
No criterion needs to be passed to move from this session type

Event sequence:
    1. The food dispensers are baited in view of the monkey (so that the monkey sees that the mean expected utility of the two apparatuses is the same)
    2. Box lights on both apparatuses light up; one in blue, the other in white (every four trials the location of each of these colours will switch side).
    3. Following a 5 s synchronisation delay, the red lever lights on both apparatuses come on simultaneously and both levers are unblocked (for max. 10 s)
    4. Monkey selects a lever and pulls, an acoustic cue sounds and at the same time both lights go out and the levers are both blocked
    5. In human condition the carousel rotates and food drops into back of the apparatus; human takes the food and hands it to the monkey. In the machine condition the carousel rotates and drops food into the front of the apparatus; monkey takes the food from the opening.
    6. 5 s inter-trial interval gives monkey time to consume food
    7. If monkey does not select a lever within 10 s, both lights go out and both levers are blocked - a 5 s inter-trial interval follows and then the next trial begins.
    8. If monkey pulls lever, repeat sequence 1-4 another 15 times

Notes on randomisation:
    + We would like to pseudo-randomise the test trials. The boxes should light up in the risky/safe colours randomly yet equally often on the left- and the right-hand side during a test session (i.e. in 8/16 trials the left box will light up as the safe option and in 8/16 trials the right box will light up as the safe option). In addition, we will cap the number of times that a box can light up consecutively in a particular colour (risky/safe) to four times. This pseudo-random lighting pattern should be different for each unique test session.
    + When it comes to the risky lever, we would like to change how the carousel reward deployment works. Ideally we would bait the risky carousel compartments 1-8 with 7 reward items and compartments 9-16 with 1 reward item and the program selects the appropriate compartment to deploy according to the unique pseudo-randomisation scheme of the session. This minimises the opportunity for experimenter error. Note that within a test session, a maximum of four jackpots (7-item rewards) and four losses (1-item rewards) can be associated with each side.
    + If the monkey chooses the safe lever over the risky one, the risky carousels of both apparatuses should also move onto the next randomly assigned compartment as well. 

The program should log:
    + Pull-latency (time between the red lever light coming on and a lever being pulled)
    + Duration, timestamp, and frequency of lever touches
    + Whether a timeout occurred
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
from monkey_list import MONKEYS, getMonkeyDBVariables, MONKEY_COLORS

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
) = getMonkeyDBVariables(MONKEYS["SCHROEDER"])
CONDITION = "quantity"
SESSION_TYPE = "test_condition"
APPARATUS_USED = "BOTH"
SESSION_NR = 6

# Depends on TEST_CONDITION_BLOCH_NUM
# True => TEST_CONDITION_BLOCH_NUM = 2, False => TEST_CONDITION_BLOCH_NUM = 1
DISTRIBUTOR_MACHINE = False

# Reward settings
WIN_REWARD_OUTCOME = 7  # Winning reward outcome
LOS_REWARD_OUTCOME = 1  # Losing reward outcome
SAF_REWARD_OUTCOME = 4  # Safe reward outcome
NON_REWARD_OUTCOME = "None"  # Timeout reward outcome

# ===== CHOICE_TRAINING Settings overwrite
CHOICE_TRAINING = True
if CHOICE_TRAINING:
    SESSION_TYPE = "choice_training_2"
    COLOR_RISK = MONKEY_COLORS["GREY"]
    COLOR_SAFE = MONKEY_COLORS["LIGHTYELLOW"]
    WIN_REWARD_OUTCOME = 0  # Winning reward outcome
    LOS_REWARD_OUTCOME = 0  # Losing reward outcome
    SAF_REWARD_OUTCOME = 2  # Safe reward outcome
# ===== CHOICE_TRAINING Settings overwrite

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

PSEUDO_RANDOM_RISK_SIDE_LEFT = util.apparatus_pseudo_random_generator(16)

# Notes on randomisation:
#    + We would like to pseudo-randomise the test trials. The
# boxes should light up in the risky/safe colours randomly yet
# equally often on the left- and the right-hand side during a
# test session [..]
temp_equal_left = util.apparatus_pseudo_random_generator(8)
temp_equal_right = util.apparatus_pseudo_random_generator(8)
temp_equal = [temp_equal_left.pop(
    0) if isLeft else temp_equal_right.pop(0) for isLeft in PSEUDO_RANDOM_RISK_SIDE_LEFT]
PSEUDO_RANDOM_RISK_OUTCOME = [
    LOS_REWARD_OUTCOME if i else WIN_REWARD_OUTCOME for i in temp_equal]


# |- PRETRIAL_LIGHT_TIME -|- LEVER_ACTIVE_TIME -| INTER_TRIAL -------|
# -- INTER_TRIAL_DELAY ---|---------------------| INTER_TRIAL_DELAY --
LEVER_ACTIVE_TIME = 20
PRETRIAL_LIGHT_TIME = 20
INTER_TRIAL_DELAY = 30  # containing PRETRIAL_LIGHT_TIME

# Apparatus
VOLUME = 90
TEST_LIGHT_COLOR = COLORS['RED']
HUMAN_LIGHT_COLOR = COLORS['RED']
APPARATUS_COLOR_LEFT = COLOR_RISK
APPARATUS_COLOR_RIGHT = COLOR_SAFE
APPARATUS_COLORS = [APPARATUS_COLOR_LEFT, APPARATUS_COLOR_RIGHT]
HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server
DEBUGLEVEL = logging.INFO
# DEBUGLEVEL = logging.DEBUG
SYCHRONISATION_DELAY = 2
DEPLOY_DELAY = 2


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
util.log_rand_info("PSEUDO_RANDOM_RISK_SIDE_LEFT",
                   PSEUDO_RANDOM_RISK_SIDE_LEFT)


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

# USE RANDOM TO ALTERNATE THE START COLORS
if util.pseudo_random_bool():
    # Colors will be switch in the first loop, since trial_id == 0,
    # but we want keep initial colors for the first loop
    APPARATUS_COLOR_LEFT, APPARATUS_COLOR_RIGHT = APPARATUS_COLOR_RIGHT, APPARATUS_COLOR_LEFT
side_risky = "LEFT" if APPARATUS_COLOR_LEFT == COLOR_RISK else "RIGHT"


def csv_event_callback(event_id, event_state, timestamp=None, event_side=None):
    logging.debug("CSV EVENT %s, %s" % (event_id, event_state,))
    csv_logger.write(
        trial_nr=trial_id+1,
        event_side=event_side,
        side_risky=side_risky,
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

# 1. The food dispensers are baited in view of the monkey (so that the
# monkey sees that the mean expected utility of the two apparatuses is the same)

# --- Set color
apparatus_left.set_test_light(False, TEST_LIGHT_COLOR)
apparatus_right.set_test_light(False, TEST_LIGHT_COLOR)
time.sleep(5)
apparatus_pulled = None
# --- Move to prepare
# safe
apparatus_left.move_to(apparatus_left.CAROUSEL_1, util.pop_deploy(
    SAFE_BAIT_PATTERN, SAF_REWARD_OUTCOME, write=False),
    monkey=DISTRIBUTOR_MACHINE, blocking=False)
apparatus_right.move_to(apparatus_right.CAROUSEL_1, util.pop_deploy(
    SAFE_BAIT_PATTERN, SAF_REWARD_OUTCOME, write=False),
    monkey=DISTRIBUTOR_MACHINE, blocking=False)
# risk
trial_id = 0
apparatus_left.move_to(apparatus_left.CAROUSEL_2, util.pop_deploy(
    RISK_BAIT_PATTERN, PSEUDO_RANDOM_RISK_OUTCOME[trial_id], write=False),
    monkey=DISTRIBUTOR_MACHINE, blocking=False)
apparatus_right.move_to(apparatus_right.CAROUSEL_2, util.pop_deploy(
    RISK_BAIT_PATTERN, PSEUDO_RANDOM_RISK_OUTCOME[trial_id], write=False),
    monkey=DISTRIBUTOR_MACHINE, blocking=False)


# start trials
for trial_id in range(0, 16):
    # Pause on p
    pause_on_p()
    # Prepare trial

    # 2. Box lights on both apparatuses light up; one in blue, the other in white (every random
    # trials the location of each of these colours will switch side).
    if PSEUDO_RANDOM_RISK_SIDE_LEFT[trial_id]:
        APPARATUS_COLOR_LEFT = COLOR_RISK
        APPARATUS_COLOR_RIGHT = COLOR_SAFE
    else:
        APPARATUS_COLOR_LEFT = COLOR_SAFE
        APPARATUS_COLOR_RIGHT = COLOR_RISK
    side_risky = "LEFT" if APPARATUS_COLOR_LEFT == COLOR_RISK else "RIGHT"
    apparatus_left.set_light(APPARATUS_COLOR_LEFT)
    apparatus_right.set_light(APPARATUS_COLOR_RIGHT)

    apparatus_left.set_human_light(False, HUMAN_LIGHT_COLOR)
    apparatus_right.set_human_light(False, HUMAN_LIGHT_COLOR)
    # --- Wait for the Hardware to reach targets
    apparatus_left.move_to_wait(apparatus_left.CAROUSEL_1)
    apparatus_left.move_to_wait(apparatus_left.CAROUSEL_2)
    apparatus_right.move_to_wait(apparatus_right.CAROUSEL_1)
    apparatus_right.move_to_wait(apparatus_right.CAROUSEL_2)

    # Trial
    logging.info("Begin Trial No. "+str(trial_id+1))
    csv_logger.write(trial_nr=trial_id+1,
                     side_risky=side_risky,
                     event_id="BEGIN_TRIAL")

    # 3. Following a 5 s synchronisation delay, the red lever lights on both
    # apparatuses come on simultaneously and both levers are unblocked
    # (for max. LEVER_ACTIVE_TIME s)

    # Start interface output
    timestamp = datetime.now()+timedelta(seconds=SYCHRONISATION_DELAY)
    timestamp += timedelta(seconds=max(PRETRIAL_LIGHT_TIME -
                           SYCHRONISATION_DELAY, 0))

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
                     side_risky=side_risky,
                     event_state=True)
    csv_logger.write(trial_nr=trial_id+1,
                     event_id="TEST_LIGHT",
                     event_side="BOTH",
                     side_risky=side_risky,
                     event_state=True)

    start = time.time()
    # --- --- OR WAIT
    event_left = apparatus_left.get_wait_lever_state_event(
        apparatus_left.LEVER_PULLED, False)
    event_right = apparatus_right.get_wait_lever_state_event(
        apparatus_right.LEVER_PULLED, False)
    lever_pulled, finish_event = event_util.OrWait(
        event_left, event_right, LEVER_ACTIVE_TIME)
    # --- --- OR WAIT

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="LEVER_OPEN",
                     event_side="BOTH",
                     side_risky=side_risky,
                     event_state=False)
    apparatus_left.set_lever_open(False)
    apparatus_right.set_lever_open(False)
    end = time.time()
    # 4. Monkey selects a lever and pulls, an acoustic cue sounds and
    # at the same time both lights go out and the levers are both blocked

    logging.info("lever_pulled: "+str(lever_pulled) +
                 " after: "+str(end - start))

    # --- --- AND WAIT
    time_to_release = max(0, LEVER_ACTIVE_TIME - (end - start))
    lever_released = apparatus_left.wait_lever_state(
        apparatus_left.LEVER_RELEASED, False, time_to_release)
    end = time.time()
    time_to_release = max(0, LEVER_ACTIVE_TIME - (end - start))
    lever_released = (lever_released and
                      apparatus_right.wait_lever_state(
                          apparatus_right.LEVER_RELEASED, False, time_to_release))
    # --- --- AND WAIT

    end = time.time()
    logging.info("lever_released: "+str(lever_released) +
                 " after: "+str(end - start))

    reward_outcome = NON_REWARD_OUTCOME
    apparatus_pulled_str = None
    if lever_pulled and lever_released:
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

        apparatus_pulled.play_sound("cash-register.mp3", volume=VOLUME)

        apparatus_pulled_color = APPARATUS_COLOR_RIGHT if apparatus_pulled_str == "RIGHT" else APPARATUS_COLOR_LEFT
        apparatus_pulled_risky = apparatus_pulled_color == COLOR_RISK
        # --- 5. In human condition the carousel rotates and food drops into back of the apparatus; human takes
        # the food and hands it to the monkey. In the machine condition the carousel rotates and drops food into
        # the front of the apparatus; monkey takes the food from the opening.

        if apparatus_pulled_risky:
            # Risky
            reward_outcome = PSEUDO_RANDOM_RISK_OUTCOME[trial_id]
            carousel = apparatus_pulled.CAROUSEL_2
            compartment = util.pop_deploy(
                RISK_BAIT_PATTERN, reward_outcome, write=True)
        else:
            # Safe
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
                     side_risky=side_risky,
                     event_state=lever_pulled and lever_released)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="REWARD_OUTCOME",
                     event_side=apparatus_pulled_str,
                     side_risky=side_risky,
                     event_state=reward_outcome)

    csv_logger.write(trial_nr=trial_id+1,
                     event_id="TEST_LIGHT",
                     event_side="BOTH",
                     side_risky=side_risky,
                     event_state=False)
    apparatus_left.set_test_light(False)
    apparatus_right.set_test_light(False)
    apparatus_left.set_light(COLORS['BLACK'])
    apparatus_right.set_light(COLORS['BLACK'])

    # Warn experimenter
    if not lever_pulled:
        session_log_side.append("NONE")
    session_log_pull.append(lever_pulled)
    session_log_warnings = session_log_warnings or not util.check_log(
        session_log_pull)

    # Wait indefinitely until the lever is up
    logging.info("Wait indefinitely until the lever is up")
    # --- --- AND WAIT
    apparatus_left.wait_lever_state(apparatus_left.LEVER_RELEASED, False)
    apparatus_right.wait_lever_state(apparatus_right.LEVER_RELEASED, False)
    # --- --- AND WAIT

    # --- Move to prepare next trial
    time.sleep(DEPLOY_DELAY)
    if trial_id < 15:
        # safe
        apparatus_left.move_to(apparatus_left.CAROUSEL_1, util.pop_deploy(
            SAFE_BAIT_PATTERN, SAF_REWARD_OUTCOME, write=False),
            monkey=DISTRIBUTOR_MACHINE, blocking=False)
        apparatus_right.move_to(apparatus_right.CAROUSEL_1, util.pop_deploy(
            SAFE_BAIT_PATTERN, SAF_REWARD_OUTCOME, write=False),
            monkey=DISTRIBUTOR_MACHINE, blocking=False)
        # risk
        apparatus_left.move_to(apparatus_left.CAROUSEL_2, util.pop_deploy(
            RISK_BAIT_PATTERN, PSEUDO_RANDOM_RISK_OUTCOME[trial_id+1], write=False),
            monkey=DISTRIBUTOR_MACHINE, blocking=False)
        apparatus_right.move_to(apparatus_right.CAROUSEL_2, util.pop_deploy(
            RISK_BAIT_PATTERN, PSEUDO_RANDOM_RISK_OUTCOME[trial_id+1], write=False),
            monkey=DISTRIBUTOR_MACHINE, blocking=False)

    logging.info("Starting inter-trial interval")
    if not lever_pulled:
        # --- 7. If monkey does not select a lever within LEVER_ACTIVE_TIME s, both lights go
        # out and both levers are blocked - a 5 s inter-trial interval follows
        # and then the next trial begins.
        # => no penalty time
        time.sleep(0)
    # --- 6. 5 s inter-trial interval gives monkey time to consume food
    time.sleep(INTER_TRIAL_DELAY-PRETRIAL_LIGHT_TIME-DEPLOY_DELAY)

    # 8. If monkey pulls lever, repeat sequence 1-4 another 15 times


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
