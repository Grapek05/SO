import sys
import csv
from scheduler import Process, RoundRobinScheduler


def load_processes(csv_path):
    processes = []
    with open(csv_path, newline="") as f:
        reader = csv.reader(f)
        for name, length, start in reader:
            processes.append(Process(name, int(length), int(start)))
    return processes


def main():
    if len(sys.argv) != 3:
        print("Usage: python rr.py <file.csv> <quantum>")
        sys.exit(1)

    csv_file = sys.argv[1]
    quantum = int(sys.argv[2])

    processes = load_processes(csv_file)
    scheduler = RoundRobinScheduler(processes, quantum)
    scheduler.run()


if __name__ == "__main__":
    main()
