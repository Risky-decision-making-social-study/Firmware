import time

from apparatus.client import ApparatusClient
from monkey_list import MONKEY_COLORS
from monkey_list import MONKEYS

# CONFIG ##################################################


HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server

# Connect to Apparatus(se)
# apparatus_left = ApparatusClient(
#     HOST_LEFT,
#     PORT,
# )
apparatus_right = ApparatusClient(
    HOST_RIGHT,
    PORT,
)

enabled = []
if 'apparatus_right' in locals():
    enabled.append(apparatus_right)
if 'apparatus_left' in locals():
    enabled.append(apparatus_left)


for apparatus in enabled:
    apparatus.init_hw()

for i in range(10):
    for apparatus in enabled:
        apparatus.deploy(apparatus_right.CAROUSEL_1,
                         0, monkey=True, blocking=False)
    time.sleep(2)
    for apparatus in enabled:
        apparatus.deploy(apparatus_right.CAROUSEL_1,
                         8, monkey=False, blocking=False)
    time.sleep(2)
    for apparatus in enabled:
        apparatus.deploy(apparatus_right.CAROUSEL_2,
                         0, monkey=True, blocking=False)
    time.sleep(2)
    for apparatus in enabled:
        apparatus.deploy(apparatus_right.CAROUSEL_2,
                         8, monkey=False, blocking=False)
    time.sleep(2)


print("DONE, CLOSING!")
for apparatus in enabled:
    apparatus.close_connection()
