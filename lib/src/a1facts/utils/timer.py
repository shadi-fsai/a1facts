import time
from colored import cprint

class Timer:
    def __init__(self):
        self.records = {}

    def start(self, label):
        if label not in self.records:
            self.records[label] = {}
        self.records[label]['start'] = time.time()

    def stop(self, label):
        if label not in self.records or 'start' not in self.records[label]:
            raise ValueError(f"Timer for '{label}' was not started.")
        self.records[label]['duration'] = time.time() - self.records[label]['start']

    def print_results(self):
        for label, record in self.records.items():
            if 'duration' in record:
                cprint(f"{label}: {record['duration']:.4f}s", "red")

timer = Timer()
