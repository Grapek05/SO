from collections import deque


class Process:
    def __init__(self, name, length, start):
        self.name = name
        self.remaining_time = length
        self.start = start


class RoundRobinScheduler:
    def __init__(self, processes, quantum):
        self.waiting_queue = deque(processes)
        self.ready_queue = deque()
        self.quantum = quantum
        self.time = 0

    def move_new_processes(self):
        while self.waiting_queue and self.waiting_queue[0].start <= self.time:
            p = self.waiting_queue.popleft()
            print(
                f"T={self.time}: New process {p.name} is waiting for execution "
                f"(length={p.remaining_time})"
            )
            self.ready_queue.append(p)

    def run(self):
        if self.waiting_queue and self.waiting_queue[0].start > 0:
            print("T=0: No processes currently available")

        while self.waiting_queue or self.ready_queue:
            self.move_new_processes()

            if not self.ready_queue:
                self.time = self.waiting_queue[0].start
                continue

            process = self.ready_queue.popleft()
            run_time = min(self.quantum, process.remaining_time)

            print(
                f"T={self.time}: {process.name} will be running for {run_time} time units. "
                f"Time left: {process.remaining_time - run_time}"
            )

            self.time += run_time
            process.remaining_time -= run_time

            self.move_new_processes()

            if process.remaining_time == 0:
                print(f"T={self.time}: Process {process.name} has been finished")
            else:
                self.ready_queue.append(process)

        print(f"T={self.time}: No more processes in queues")
