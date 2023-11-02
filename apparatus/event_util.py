from threading import Event, Thread
from typing import List, Tuple

thread_list: List[Thread] = []


def thread_func(event: Event, cond: Event, finishes: List, stop_thread):
    while True:
        if stop_thread():
            break
        event.wait(1)
        if event.is_set():
            finishes.append(event)
            cond.set()


def OrWait(event1: Event, event2: Event, timeout=None) -> Tuple[bool, Event]:
    cond = Event()
    finishes = []

    _stop_async_send_thread = False
    thread1: Thread = Thread(
        target=thread_func, args=(event1, cond, finishes, lambda: _stop_async_send_thread,), daemon=True).start()
    thread_list.append(thread1)
    thread2: Thread = Thread(
        target=thread_func, args=(event2, cond, finishes, lambda: _stop_async_send_thread,), daemon=True).start()
    thread_list.append(thread2)

    did_not_timeout = cond.wait(timeout)
    _stop_async_send_thread = True

    if did_not_timeout:
        return did_not_timeout, finishes[0]
    else:
        return did_not_timeout, None


def joinThreads():
    for t in thread_list:
        if t is not None and t.is_alive():
            t.join()
