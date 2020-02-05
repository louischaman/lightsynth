from collections import deque
import time
import numpy

class delay_single:
    def __init__(self, delay_length, feedback, wet_dry, realtime=False, buffer_size=100):
        self.delay_length = delay_length
        self.feedback = feedback
        self.wet_dry = wet_dry
        self.realtime = realtime
        self.input_buffer = deque(maxlen=buffer_size)
        for i in range(buffer_size):
            self.input_buffer.append([0,0])

    def delay_input(self, val, time_now=None):
        if self.realtime:
            time_now = time.time()
        
        self.input_buffer.append([time_now, val])

    def feedback_line(self, time_now=None):
        if self.realtime:
            time_now = time.time()
        val = None
        if len(self.input_buffer) == 0:
            return None
        while self.input_buffer[0][0]< (time_now - self.delay_length):
            self.input_buffer.popleft()
            if len(self.input_buffer) == 0:
                return None
        val = self.input_buffer[0][1]
        return val

    def delay_output(self, val, time_now=None):
        feedback_val = self.feedback_line(time_now=time_now)
        self.delay_input(feedback_val* self.feedback + val , time_now=time_now)
        return val + feedback_val * self.wet_dry


dl = delay_single(3,0.5,0.5)
print(dl.delay_output(1,1))

for i in range(20):
    print(dl.delay_output(0,i))

        


