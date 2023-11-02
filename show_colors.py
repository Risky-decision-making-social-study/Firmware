import time

from apparatus.client import ApparatusClient
from monkey_list import MONKEY_COLORS

# CONFIG ##################################################

ON_TIME = 5

HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server

# Connect to Apparatus(se)
apparatus = ApparatusClient(
    HOST_LEFT,
    PORT,
)

apparatus.init_hw()

for color in MONKEY_COLORS.keys():
    print(color)
    apparatus.set_light(MONKEY_COLORS[color])
    apparatus.set_human_light(True, MONKEY_COLORS[color])
    apparatus.set_test_light(True, MONKEY_COLORS[color])
    time.sleep(ON_TIME)


apparatus.close_connection()
