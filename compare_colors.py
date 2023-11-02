import time

from apparatus.client import ApparatusClient
from monkey_list import MONKEY_COLORS
from monkey_list import MONKEYS

# CONFIG ##################################################


HOST_LEFT = '192.168.0.2'  # The server's hostname or IP address
HOST_RIGHT = '192.168.0.3'  # The server's hostname or IP address
PORT = 9001        # The port used by the server

# Connect to Apparatus(se)
apparatus_left = ApparatusClient(
    HOST_LEFT,
    PORT,
)
apparatus_right = ApparatusClient(
    HOST_RIGHT,
    PORT,
)

apparatus_left.init_hw()
apparatus_right.init_hw()


def set_all(apparatus, color):
    apparatus.set_light(color)
    apparatus.set_human_light(True, color)
    apparatus.set_test_light(True, color)


my_colors = False
if my_colors:
    set_all(apparatus_right, MONKEY_COLORS["LIGHTYELLOW"])
    set_all(apparatus_left, MONKEY_COLORS["GREEN1"])
    time.sleep(30)


all_monkeys = True
compare_color = MONKEY_COLORS["LIGHTYELLOW"]
ON_TIME = 4
if all_monkeys:
    for monkey in MONKEYS:
        print(monkey)
        values = MONKEYS[monkey]
        for x in ["COLOR_SAFE", "COLOR_RISK"]:
            print("%s (%s) and LIGHTYELLOW" % (
                x,
                list(MONKEY_COLORS.keys())[
                    list(MONKEY_COLORS.values()).index(values[x])]
            ))
            set_all(apparatus_left, compare_color)
            set_all(apparatus_right, values[x])
            time.sleep(ON_TIME)

print("DONE, CLOSING!")
apparatus_left.close_connection()
apparatus_right.close_connection()


for color in MONKEY_COLORS.keys():
    print(color)
    set_all(apparatus_right, MONKEY_COLORS[color])
    set_all(apparatus_left, MONKEY_COLORS[color])
    time.sleep(1)
