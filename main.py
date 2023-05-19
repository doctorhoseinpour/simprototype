from scipy.stats import poisson, expon
import random
import numpy as np

X = 10
Y = 10
PROCESSORS_NUM = 1
SERVICE_POLICY = "FIFO"
T = 100
LENGTH_LIMIT = 5

class Task:
    ID = 0
    TIME = 0

    def __init__(self, service_time, interarrival_time, priority):
        self.id = Task.ID
        self.service_time = service_time
        self.interarrival_time = interarrival_time
        self.priority = priority
        self.arrival_time = Task.TIME
        self.time_service_begins = 0
        self.time_waits_in_queue = 0
        self.time_service_ends = 0
        self.time_customer_spends_in_system = 0
        self.idle_time_of_server = 0
        Task.ID += 1
        Task.TIME += interarrival_time

class Router:
    
    def __init__(self, queue_capacity, X, Y):
        self.queue_capacity = queue_capacity
        self.X = X
        self.Y = Y
        self.total_tasks = []
        self.queue = []
        self.queue_average_length = 0

    def generate_tasks(self):
        interarrival_time = poisson.rvs(mu=self.X, size=1)[0]
        service_time = expon.rvs(scale=self.Y, size=1)[0]
        priority = random.choices(['HIGH', 'MEDIUM', 'LOW'], weights=(0.2, 0.3, 0.5), k=1)[0]
        task = Task(service_time, interarrival_time, priority)
        self.total_tasks.append(task)
        return task.arrival_time


class Simulation:

    def __init__(self, X, Y, PROCESSORS_NUM, SERVICE_POLICY, T, LENGTH_LIMIT):
        self.X = X
        self.Y = Y
        self.PROCESSORS_NUM = PROCESSORS_NUM
        self.SERVICE_POLICY = SERVICE_POLICY
        self.T = T
        self.LENGTH_LIMIT = LENGTH_LIMIT
        self.time = 0
        self.router = Router(self.LENGTH_LIMIT, self.X, self.Y)
        ##
        self.times = [0] * PROCESSORS_NUM
        self.queues_average_time = 0
        self.queues_average_time_per_cpu = [0] * PROCESSORS_NUM
        self.idle_time_of_the_cpus = 0
        self.idle_time_of_the_cpus_lst = [0] * PROCESSORS_NUM
        self.cpus_efficiency = 0
        self.cpus_efficiencies = [0] * PROCESSORS_NUM
        self.dropped_packets_num = 0

    def FIFO_policy(self):
        if len(self.router.queue) > 0:
            return self.router.queue.pop(0)

    def WRR_policy(self):
        if len(self.router.queue) > 0:
            pr = random.choices(['HIGH', 'MEDIUM', 'LOW'], weights=(0.2, 0.3, 0.5), k=1)[0]
            i = 0
            for t in router.queue:
                if t.priority == pr:
                    return self.router.queue.pop(i)
                i += 1
            pr2 = random.choices(['HIGH', 'MEDIUM', 'LOW'], weights=(0.2, 0.3, 0.5), k=1)[0]
            while pr2 == pr:
                pr2 = random.choices(['HIGH', 'MEDIUM', 'LOW'], weights=(0.2, 0.3, 0.5), k=1)[0]
            i = 0
            for t in router.queue:
                if t.priority == pr2:
                    return self.router.queue.pop(i)
                i += 1
            pr3 = random.choices(['HIGH', 'MEDIUM', 'LOW'], weights=(0.2, 0.3, 0.5), k=1)[0]
            while pr3 == pr2 or pr3 == pr2:
                pr2 = random.choices(['HIGH', 'MEDIUM', 'LOW'], weights=(0.2, 0.3, 0.5), k=1)[0]
            i = 0
            for t in router.queue:
                if t.priority == pr3:
                    return self.router.queue.pop(i)
                i += 1
            
    
    def NPPS_policy(self):
        if len(self.router.queue) > 0:
            i = 0
            for t in router.queue:
                if t.priority == "HIGH":
                    return self.router.queue.pop(i)
                i += 1

            i = 0
            for t in router.queue:
                if t.priority == "MEDIUM":
                    return self.router.queue.pop(i)
                i += 1
            
            i = 0
            for t in router.queue:
                if t.priority == "LOW":
                    return self.router.queue.pop(i)
                i += 1

    def dispatcher(self):
        task = self.FIFO_policy()
        if self.SERVICE_POLICY == "FIFO":
            task = self.FIFO_policy()
        elif self.SERVICE_POLICY == "WRR":
            task = self.WRR_policy()
        elif self.SERVICE_POLICY == "NPPS":
            task = self.NPPS_policy()

        return task

    def dispatcher_optional(self):
        turn = random.choices(['RRT1', 'RRT2', 'FCFS'], weights=(0.8, 0.1, 0.1), k=1)[0]
        task = None
        if turn == 'RRT1':
            task = self.RRT1_policy()
            turn = 1
        elif turn == 'RRT2':
            task = self.RRT1_policy()
            turn = 2
        elif turn == 'FCFS':
            task = self.RRT1_policy()
            turn = 3

        return task, turn

    def simulate(self):
        t = 0
        while t <= self.T:
            t = self.router.generate_tasks()

        itr = 0
        wait_itr = 0
        wait_itrs = [0.01] * PROCESSORS_NUM

        while len(self.router.queue) <= self.router.queue_capacity:
            for ta in range(len(self.router.total_tasks)):
                if len(self.router.queue) <= self.router.queue_capacity:
                    self.router.queue.append(self.router.total_tasks.pop(ta))
                    break


        last_time = self.time
        while self.time < self.T:

            if len(self.router.total_tasks) > 0:
                if len(self.router.queue) <= self.router.queue_capacity:
                    self.router.queue.append(self.router.total_tasks.pop(0))
                    continue
                else: 
                    self.dropped_packets_num += 1

            task = self.dispatcher()
            if task is None:
                last_time = self.time
                self.time += 1
                self.times = [x + 1 for x in self.times]
                continue
            arrival_time = task.arrival_time
            service_time = task.service_time
            min_time = min(x for x in self.times if x is not np.nan)
            min_time_arg = np.nanargmin(self.times, axis=0)

            if arrival_time >= min_time:
                task.time_service_begins = arrival_time
                task.time_waits_in_queue = 0
                task.idle_time_of_server = arrival_time - min_time

            else:  # arrival_time < self.time
                task.time_service_begins = min_time
                task.time_waits_in_queue = min_time - arrival_time
                task.idle_time_of_server = 0

            # average time spend in the queue
            wait_itr += 1
            wait_itrs[min_time_arg] += 1

            task.time_service_ends = task.time_service_begins + task.service_time   

            task.time_customer_spends_in_system = task.time_service_ends - arrival_time
            min_time = task.time_service_begins + task.service_time
            last_time = self.time
            self.times[min_time_arg] = min_time
            self.time = max(x for x in self.times if x is not np.nan)

            # average length of the queue
            self.router.queue_average_length += len(self.router.queue)
            # average time spend in the queue
            self.queues_average_time += task.time_waits_in_queue
            self.queues_average_time_per_cpu[min_time_arg] += task.time_waits_in_queue
            # idle time of the cpus
            self.idle_time_of_the_cpus += task.idle_time_of_server
            self.idle_time_of_the_cpus_lst[min_time_arg] += task.idle_time_of_server
            itr += 1
            print(
                f'ID: {task.id}, service_time: {task.service_time}, interarrival_time: {task.interarrival_time}, priority: {task.priority}, arrival_time: {task.arrival_time}, time_service_begins: {task.time_service_begins}, time_waits_in_queue: {task.time_waits_in_queue}, time_service_ends: {task.time_service_ends}, time_customer_spends_in_system: {task.time_customer_spends_in_system}, idle_time_of_server: {task.idle_time_of_server}')
        print('Times:', self.times)

        # average length of the queue
        self.router.queue_average_length /= itr
        # average time spend in the queue
        self.queues_average_time /= wait_itr
        self.queues_average_time_per_cpu = [a / b for a, b in zip(self.queues_average_time_per_cpu, wait_itrs)]
        # cpu efficiency
        self.cpus_efficiency = self.idle_time_of_the_cpus / self.T
        self.cpus_efficiencies = [a / b for a, b in zip(self.idle_time_of_the_cpus_lst, [self.T]*len(self.idle_time_of_the_cpus_lst))]
       

simulation = Simulation(X, Y, PROCESSORS_NUM, SERVICE_POLICY, T, LENGTH_LIMIT)
simulation.simulate()
print('A) Average Length of the Queues: PriorityQueue -> ', simulation.router.queue_average_length)
print('B) Average Time Spend in Queues -> ', simulation.queues_average_time
      , '\n\t Per CPU ->', simulation.queues_average_time_per_cpu)
print('C) Average Efficiency of CPUs -> ', simulation.cpus_efficiency
      , '\n\t Per CPU ->', simulation.cpus_efficiencies)
print('C) Number of Dropped Packets -> ', simulation.dropped_packets_num)