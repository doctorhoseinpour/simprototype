import random
import numpy as np
from typing import List
class Host:
    def __init__(self, lambda_poisson, t):
        self.lambda_poisson = lambda_poisson
        self.t = t
    
    def generate_packet_schedule(self):
        packet_times = []
        current_time = 0
        while current_time < self.t:
            current_time += np.random.exponential(1 / self.lambda_poisson)
            packet_times.append(current_time)
        return packet_times


class Packet:
    def __init__(self):
        self.arrival_time = 0
        self.start_time = 0
        self.finish_time = 0
    
    def get_time_in_queue(self):
        return self.start_time - self.finish_time

class Router:
    def __init__(self, lambda_exp, processor_count):
        self.lambda_exp = lambda_exp
        self.processor_count = processor_count
        self.free_processor_count = processor_count
        self.queue: List[Packet] = []
        self.wrr_queue_1: List[Packet] = []
        self.wrr_queue_2: List[Packet] = []
        self.wrr_queue_3: List[Packet] = []
        self.current_packet: Packet = None

    def get_packet_finish_time(self, packet: Packet):
        return np.random.exponential(1 / self.lambda_poisson) + packet.start_time
    
    def pop_queue(self):
        