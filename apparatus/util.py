from itertools import count
import logging
import os
import random
import subprocess
import time
from datetime import datetime
from typing import List
import yaml

######################################################################
# General system and software information
######################################################################


def get_cpu_info():
    try:
        f = open('/proc/cpuinfo', 'rb')
        data = f.read()
        f.close()
    except (IOError, OSError) as e:
        logging.debug("Exception on read /proc/cpuinfo: %s",
                      str(e))
        return "?"
    lines = [l.split(b':', 1) for l in data.split(b'\n')]
    lines = [(l[0].strip(), l[1].strip()) for l in lines if len(l) == 2]
    core_count = [k for k, v in lines].count("processor")
    model_name = dict(lines).get("model name", "?")
    return "%d core %s" % (core_count, model_name)


def get_version_from_file(apparatus_src):
    try:
        with open(os.path.join(apparatus_src, '.version')) as h:
            return h.read().rstrip()
    except IOError:
        pass
    return "?"


def get_git_version(from_file=True):
    apparatus_src = os.path.dirname(__file__)

    # Obtain version info from "git" program
    gitdir = os.path.join(apparatus_src, '..')
    prog = ('git', '-C', gitdir, 'describe', '--always',
            '--tags', '--long', '--dirty')
    try:
        process = subprocess.Popen(prog, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        ver, err = process.communicate()
        retcode = process.wait()
        if retcode == 0:
            return ver.strip()
        else:
            logging.debug("Error getting git version: %s", err)
    except OSError:
        logging.debug("Exception on run: %s", str(e))

    if from_file:
        return get_version_from_file(apparatus_src)
    return "?"


def wait_till(timestamp):
    delay = (timestamp - datetime.now()).total_seconds()
    time.sleep(delay)


def pseudo_random_bool():
    return bool(random.getrandbits(1))


def pseudo_random_generator(num: int):
    return [pseudo_random_bool() for i in range(num)]


def longest(s, filter=None):
    maximum = count = 0
    current = ''
    for c in s:
        if c == current and (filter is None or c == filter):
            count += 1
        else:
            count = 1
            current = c
        maximum = max(count, maximum)
    return maximum


def even(num):
    return num % 2 == 0


def log_rand_info(name, llist):
    lrow = longest(llist)
    lrow_true = longest(llist)
    lrow_false = longest(llist)
    llen = len(llist)

    e_count = {}
    for i in list(set(llist)):
        e_count[str(i)] = llist.count(i)

    elements_count = yaml.dump(e_count)

    logging.info(
        "apparatus_pseudo_random_generator info for %s:\n" % (name,)
        + "%s\n" % (llist[0:len(llist) if len(llist) < 32 else 32],)
        + "%s -> %d\n" % ("lrow", lrow)
        + "%s -> %d\n" % ("lrow_true", lrow_true)
        + "%s -> %d\n" % ("lrow_false", lrow_false)
        + "%s -> %d\n" % ("llen", llen)
        + "%s ->\n%s" % ("elements_count:", elements_count)
        + "---"
    )


def apparatus_pseudo_random_generator_check(rlist: list, num: int, longest_row=4):
    return longest(rlist) <= longest_row and rlist.count(True) == int(num/2) or not even(num) and rlist.count(True) in [int(num/2), int(num/2)+1]


def apparatus_pseudo_random_generator(num: int, longest_row=4):
    count = 0
    while True:
        count += 1
        rlist = pseudo_random_generator(num)
        if apparatus_pseudo_random_generator_check(rlist, num, longest_row):
            print(count)
            return rlist


def check_log(pull_log: list, side_log: list = None):
    if pull_log.count(False) >= 6:
        logging.warn("monkey did not pull lever at least 6 times!")
        return False
    if longest(pull_log, False) >= 3 and pull_log[-1] == False:
        logging.warn(
            "monkey did not pull lever at least 3 times in a row!")
        return False
    if side_log is not None and (side_log.count("LEFT") >= 12 or side_log.count("RIGHT") >= 12):
        logging.warn(
            "side-bias discovered! The monkey pulled the lever on one side at least 12")
        return False
    return True


def pop_deploy(list: List, value, write=False):
    try:
        index = list.index(value)
    except ValueError:
        logging.error("No compartments with this bait available!")
        return -1
    if write:
        list[index] = 0
    return index


def random_list_modifier(pull_log, random_list):
    mod_random_list = random_list.copy()

    temp = [random_list[i] if pull_log[i]
            else 0 for i in range(min(len(pull_log), len(random_list)))]

    values = list(set(random_list))

    upper_threshold = 3
    lower_threshold = 1

    threshold = max(lower_threshold, min(
        upper_threshold, len(random_list)-len(pull_log)))
    offset = temp.count(values[0])-temp.count(values[1])
    print(offset)
    next_value_suggestion = values[0] if offset < 0 else values[1]
    next_value_apply = abs(temp.count(values[0]) -
                           temp.count(values[1])) >= threshold
    if next_value_apply and len(pull_log) < len(random_list):
        if mod_random_list[len(pull_log)] != next_value_suggestion:
            mod_random_list[len(pull_log)] = next_value_suggestion
            print("Wrote %d to %d" % (next_value_suggestion, len(pull_log),))

    return mod_random_list


# ---
def main():
    import itertools
    ignore_random_rules = True

    all_true_false = itertools.product([True, False], repeat=8)
    all_one_seven = itertools.product([1, 7], repeat=8)
    count = []
    for true_false in all_true_false:
        for one_seven in all_one_seven:
            if ignore_random_rules and len(list(set(one_seven))) == 2 or apparatus_pseudo_random_generator_check(list(one_seven), 8):
                print(list(one_seven))
                for a in range(8):
                    ret = random_list_modifier(
                        list(true_false)[0:a], list(one_seven))
                    count.append(list(one_seven) == ret)
                    if list(one_seven) != ret:
                        pass

    print(len(count))
    print(count.count(True))


if __name__ == "__main__":
    main()
