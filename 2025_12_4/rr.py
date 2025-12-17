#!/usr/bin/env python3
import sys
import csv
from collections import deque


class Process:
    def __init__(self, name, length, start):
        self.name = name
        self.length = length
        self.remaining = length
        self.start = start

    def __repr__(self):
        return f"{self.name}(remaining={self.remaining}, start={self.start})"


class RoundRobinScheduler:
    def __init__(self, processes, quantum):
        self.waiting = deque(processes)   # procesy jeszcze nieuruchomione
        self.ready = deque()              # kolejka RR
        self.quantum = quantum
        self.time = 0

    def add_new_processes(self):
        """Przenosi procesy, których czas startu <= aktualny czas"""
        while self.waiting and self.waiting[0].start <= self.time:
            p = self.waiting.popleft()
            print(f"T={self.time}: New process {p.name} is waiting for execution (length={p.length})")
            self.ready.append(p)

    def run(self):
        if not self.waiting:
            print("T=0: No processes currently available")
            return

        while self.waiting or self.ready:
            self.add_new_processes()

            if not self.ready:
                # brak gotowych procesów – przeskok czasu
                if self.waiting:
                    if self.time < self.waiting[0].start:
                        print(f"T={self.time}: No processes currently available")
                        self.time = self.waiting[0].start
                continue

            process = self.ready.popleft()

            run_time = min(self.quantum, process.remaining)
            process.remaining -= run_time

            print(
                f"T={self.time}: {process.name} will be running for {run_time} time units. "
                f"Time left: {process.remaining}"
            )

            self.time += run_time

            # w trakcie działania mogły pojawić się nowe procesy
            self.add_new_processes()

            if process.remaining == 0:
                print(f"T={self.time}: Process {process.name} has been finished")
            else:
                self.ready.append(process)

        print(f"T={self.time}: No more processes in queues")


def load_processes_from_csv(path):
    processes = []
    with open(path, newline="") as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            name, length, start = row
            processes.append(Process(name, int(length), int(start)))
    return processes


def main():
    if len(sys.argv) != 3:
        print("Usage: ./rr.py <file.csv> <quantum>")
        sys.exit(1)

    csv_path = sys.argv[1]
    quantum = int(sys.argv[2])

    processes = load_processes_from_csv(csv_path)
    scheduler = RoundRobinScheduler(processes, quantum)
    scheduler.run()


if __name__ == "__main__":
    main()