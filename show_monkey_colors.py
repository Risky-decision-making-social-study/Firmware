import time

from apparatus.client import ApparatusClient
from monkey_list import MONKEY_COLORS, MONKEYS, getMonkeyDBVariablesSampling2

# CONFIG ##################################################

ON_TIME = 5

HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server

# Connect to Apparatus(se)
apparatus_right = ApparatusClient(
    HOST_RIGHT,
    PORT,
)
# apparatus_left = ApparatusClient(
#     HOST_LEFT,
#     PORT,
# )

apparatus_right.init_hw()
# apparatus_left.init_hw()
apparatus_right.set_lever_open(True)

for monkey in MONKEYS:
    (
        SUBJECT_NAME,
        SEX,
        AGE,
        COLOR_RISK,
        COLOR_SAFE,
        DISTRIBUTOR_FIRST,
        CONTROLLER_ID,
        DISTRIBUTOR_ID,
    ) = getMonkeyDBVariablesSampling2(MONKEYS[monkey])
    print(SUBJECT_NAME)
    apparatus_right.set_light(COLOR_RISK)
    apparatus_right.set_human_light(True, COLOR_SAFE)
    # apparatus_left.set_light(COLOR_SAFE)
    time.sleep(ON_TIME)


apparatus_right.close_connection()
# apparatus_left.close_connection()
