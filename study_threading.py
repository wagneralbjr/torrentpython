import threading
import queue
import random
from time import sleep

q = queue.Queue()


def worker():
    while True:
        item = q.get()
        print(f"Working in {item}")
        print(f"Finished {item}")
        sleep(0.5)
        q.task_done()


def producer():
    while True:
        choice_random = random.choice(range(1000))
        q.put(choice_random)
        print(f"Put random item {choice_random}")
        sleep(0.2)


threading.Thread(target=producer, daemon=True).start()
threading.Thread(target=worker, daemon=True).start()


q.join()
print("Everything done")
