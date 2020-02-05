import time
import threading
import copy

class waitRun(threading.Thread):
    def __init__(self, wait_secs, run_fn):
        super(waitRun,self).__init__()
        self.wait_secs = wait_secs
        self.run_fn = run_fn

    def run(self):
        time.sleep(self.wait_secs)
        self.run_fn()

class appendMsgSequence(threading.Thread):
    def __init__(self, queue, msg_sequence, repeat=None, bpm=None, auto_sort=True):
        super(appendMsgSequence,self).__init__()
        if bpm is not None:
            for i, msg in enumerate(msg_sequence):
                msg_sequence[i] = (float(msg[0]) * 60/bpm, msg[1])
            if repeat is not None:
                repeat = repeat * 60/bpm

        if repeat is not None:   
            print(repeat)
            max_sequence_time = max(msg[0] for msg in msg_sequence)
            if max_sequence_time >= repeat:
                raise(ValueError("max sequence time is more than repeat time"))

        self.queue = queue
        if auto_sort:
            self.msg_sequence = sorted(msg_sequence, key=lambda x: x[0])[::-1]
        else:
            self.msg_sequence = msg_sequence#[::-1]
        self.msg_sequence_original = copy.copy(self.msg_sequence)
        self.repeat = repeat
        self._stop_event = threading.Event()

    def stop(self):
        self._stop_event.set()

    def stopped(self):  
        return self._stop_event.is_set()

    def run(self):
        start_time = time.time()
        while len(self.msg_sequence)>0 :
            timing, msg = self.msg_sequence.pop()
            while ((time.time() - start_time) < timing):
                if self.stopped(): return
                time.sleep(0.001)
            self.queue.append(msg)
            if (len(self.msg_sequence) == 0) and (self.repeat is not None):
                while ((time.time() - start_time) < self.repeat):
                    time.sleep(0.001)
                    if self.stopped(): return
                self.msg_sequence = copy.copy(self.msg_sequence_original)
                start_time = start_time + self.repeat


if __name__=='__main__':
    queue = []
    msg_list = [(0, 'hello'), (1, 'hello'),(2, 'hello'),(3, 'goodbye')]
    ms = appendMsgSequence(queue, msg_list, 4, 120)
    ms.start()


    try:
        while 1:
            if len(queue)>0:
                print(queue.pop())
    except KeyboardInterrupt:
        # quit
        ms.stop()


    # from signal import signal, SIGINT
    # from sys import exit
    # import time


    # class simple():
    #     def __init__(self):
    #         signal(SIGINT, self.handler)
    #     def handler(self, signal_received, frame):
    #         # Handle any cleanup here
    #         print('SIGINT or CTRL-C detected. Exiting gracefully')
    #         self.stop()
    #         exit(0)
    #     def wait(self):
    #         while 1:
    #             time.sleep(0.1)
    #     def stop(self):
    #         print('stopping')

    # simple().wait()

    # if __name__ == '__main__':
    #     # Tell Python to run the handler() function when SIGINT is recieved
        