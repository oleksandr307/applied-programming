import random
import time
import threading
from collections import deque

class MessageQueue:
    def __init__(self):
        self.queue = deque()
        self.lock = threading.Lock()
    
    def add_message(self, message):
        with self.lock:
            self.queue.append(message)
            print(f"[Додано] {message}")
    
    def get_message(self):
        with self.lock:
            if self.queue:
                return self.queue.popleft()
            return None

class MessageGenerator(threading.Thread):
    def __init__(self, queue, t1, num_messages=20):
        super().__init__()
        self.queue = queue
        self.t1 = t1
        self.num_messages = num_messages
        self.running = True
    
    def run(self):
        for i in range(self.num_messages):
            if not self.running:
                break
            interval = random.randint(1, self.t1)
            time.sleep(interval)
            message = f"Повідомлення {i+1}"
            self.queue.add_message(message)
        print("\n[Генератор] Всі повідомлення надіслано")
        self.running = False

class MessageProcessor(threading.Thread):
    def __init__(self, queue, t2):
        super().__init__()
        self.queue = queue
        self.t2 = t2
        self.running = True
    
    def run(self):
        processed = 0
        while self.running:
            message = self.queue.get_message()
            if message:
                process_time = random.randint(1, self.t2)
                time.sleep(process_time)
                print(f"[ОБРОБЛЕНО] {message} (час: {process_time}с)")
                processed += 1
            else:
                if not self.generator_running():
                    break
                time.sleep(0.1)
        print(f"\n[Обробник] Всього оброблено: {processed}")
    
    def generator_running(self):
        for thread in threading.enumerate():
            if isinstance(thread, MessageGenerator) and thread.running:
                return True
        return False
    
    def stop(self):
        self.running = False

if __name__ == "__main__":
    print("="*50)
    print("ЗАДАЧА 31.3 - ОБРОБКА ПОВІДОМЛЕНЬ У ЧЕРЗІ")
    print("="*50)
    t1, t2, num_messages = 3, 2, 10
    queue = MessageQueue()
    generator = MessageGenerator(queue, t1, num_messages)
    processor = MessageProcessor(queue, t2)
    generator.start()
    processor.start()
    generator.join()
    time.sleep(1)
    processor.stop()
    processor.join()
    print("\nРОБОТУ ЗАВЕРШЕНО")
