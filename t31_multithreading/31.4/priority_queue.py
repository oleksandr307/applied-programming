import random
import time
import threading
from collections import deque

class PriorityMessageQueue:
    def __init__(self):
        self.normal_queue = deque()
        self.priority_queue = deque()
        self.lock = threading.Lock()
    
    def add_message(self, message, is_priority=False):
        with self.lock:
            if is_priority:
                self.priority_queue.append(message)
                print(f"[Додано ПРIОРИТЕТНЕ] {message}")
            else:
                self.normal_queue.append(message)
                print(f"[Додано звичайне] {message}")
    
    def get_message(self):
        with self.lock:
            if self.priority_queue:
                return self.priority_queue.popleft(), True
            elif self.normal_queue:
                return self.normal_queue.popleft(), False
            return None, False

class PriorityMessageGenerator(threading.Thread):
    def __init__(self, queue, t1, num_messages=20, priority_ratio=0.3):
        super().__init__()
        self.queue = queue
        self.t1 = t1
        self.num_messages = num_messages
        self.priority_ratio = priority_ratio
        self.running = True
    
    def run(self):
        for i in range(self.num_messages):
            if not self.running:
                break
            interval = random.randint(1, self.t1)
            time.sleep(interval)
            is_priority = random.random() < self.priority_ratio
            if is_priority:
                message = f"Повідомлення {i+1} (ПРIОРИТЕТНЕ)"
            else:
                message = f"Повідомлення {i+1} (звичайне)"
            self.queue.add_message(message, is_priority)
        print("\n[Генератор] Всі повідомлення надіслано")
        self.running = False

class PriorityMessageProcessor(threading.Thread):
    def __init__(self, queue, t2):
        super().__init__()
        self.queue = queue
        self.t2 = t2
        self.running = True
        self.processed_priority = 0
        self.processed_normal = 0
    
    def run(self):
        while self.running:
            message, is_priority = self.queue.get_message()
            if message:
                process_time = random.randint(1, self.t2)
                time.sleep(process_time)
                msg_type = "ПРIОРИТЕТНЕ" if is_priority else "звичайне"
                print(f"[ОБРОБЛЕНО {msg_type}] {message} (час: {process_time}с)")
                if is_priority:
                    self.processed_priority += 1
                else:
                    self.processed_normal += 1
            else:
                if not self.generator_running():
                    break
                time.sleep(0.1)
        print(f"\n[Обробник] Пріоритетних: {self.processed_priority}, Звичайних: {self.processed_normal}")
    
    def generator_running(self):
        for thread in threading.enumerate():
            if isinstance(thread, PriorityMessageGenerator) and thread.running:
                return True
        return False
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    print("="*50)
    print("ЗАДАЧА 31.4 - ПРIОРИТЕТНА ОБРОБКА ПОВІДОМЛЕНЬ")
    print("="*50)
    t1, t2, num_messages, priority_ratio = 3, 2, 15, 0.4
    queue = PriorityMessageQueue()
    generator = PriorityMessageGenerator(queue, t1, num_messages, priority_ratio)
    processor = PriorityMessageProcessor(queue, t2)
    generator.start()
    processor.start()
    generator.join()
    time.sleep(1)
    processor.stop()
    processor.join()
    print("\nРОБОТУ ЗАВЕРШЕНО")
