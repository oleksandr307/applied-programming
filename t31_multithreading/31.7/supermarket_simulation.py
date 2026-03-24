import random
import matplotlib.pyplot as plt
from collections import deque

class Cashier:
    def __init__(self, cashier_id, is_reserve=False):
        self.id = cashier_id
        self.is_reserve = is_reserve
        self.busy_until = 0
        self.queue = deque()
        self.total_served = 0
        self.on_break = False
        self.break_end_time = 0

class SupermarketSimulation:
    def __init__(self, N, m, k, t1, t2, t3, t4, l_max, sim_time=10000):
        self.N = N
        self.m = m
        self.k = k
        self.t1 = t1
        self.t2 = t2
        self.t3 = t3
        self.t4 = t4
        self.l_max = l_max
        self.sim_time = sim_time
        self.cashiers = [Cashier(i) for i in range(m)]
        self.reserve_cashiers = []
        self.max_queue_history = []
        self.reserve_added_times = []
        self._distribute_initial_customers()
    
    def _distribute_initial_customers(self):
        per = self.k // len(self.cashiers)
        rem = self.k % len(self.cashiers)
        for i, c in enumerate(self.cashiers):
            for _ in range(per + (1 if i < rem else 0)):
                c.queue.append(0)
    
    def add_customer(self, t):
        cs = self.cashiers + self.reserve_cashiers
        if cs:
            random.choice(cs).queue.append(t)
    
    def add_reserve(self, t):
        if len(self.cashiers) + len(self.reserve_cashiers) < self.N:
            self.reserve_cashiers.append(Cashier(len(self.cashiers) + len(self.reserve_cashiers), True))
            self.reserve_added_times.append(t)
            return True
        return False
    
    def redistribute(self):
        if not self.reserve_cashiers:
            return
        all_c = self.cashiers + self.reserve_cashiers
        longest = max(all_c, key=lambda c: len(c.queue))
        new_c = self.reserve_cashiers[-1]
        to_move = len(longest.queue) // 2
        for _ in range(to_move):
            if longest.queue:
                new_c.queue.append(longest.queue.popleft())
    
    def process_breaks(self, t):
        for c in self.cashiers + self.reserve_cashiers:
            if not c.on_break and c.busy_until <= t and random.random() < 1.0/self.t3:
                c.on_break = True
                c.break_end_time = t + random.randint(1, self.t4)
            if c.on_break and c.break_end_time <= t:
                c.on_break = False
    
    def run(self):
        t = 0
        next_cust = random.randint(1, self.t1)
        service_end = {}
        all_c = self.cashiers + self.reserve_cashiers
        for c in all_c:
            if c.queue and not c.on_break:
                service_end[c.id] = t + random.randint(1, self.t2)
        
        while t < self.sim_time:
            next_svc = float('inf')
            next_svc_c = None
            for cid, et in service_end.items():
                if et < next_svc:
                    next_svc = et
                    for c in all_c:
                        if c.id == cid:
                            next_svc_c = c
                            break
            next_brk = float('inf')
            next_brk_c = None
            for c in all_c:
                if c.on_break and c.break_end_time < next_brk:
                    next_brk = c.break_end_time
                    next_brk_c = c
            t = min(next_cust, next_svc, next_brk)
            if next_cust == t:
                self.add_customer(t)
                next_cust = t + random.randint(1, self.t1)
            elif next_svc == t and next_svc_c:
                if next_svc_c.queue:
                    next_svc_c.queue.popleft()
                    next_svc_c.total_served += 1
                if next_svc_c.queue and not next_svc_c.on_break:
                    service_end[next_svc_c.id] = t + random.randint(1, self.t2)
                elif next_svc_c.id in service_end:
                    del service_end[next_svc_c.id]
            elif next_brk == t and next_brk_c:
                next_brk_c.on_break = False
                if next_brk_c.queue:
                    service_end[next_brk_c.id] = t + random.randint(1, self.t2)
            all_c = self.cashiers + self.reserve_cashiers
            max_q = max((len(c.queue) for c in all_c), default=0)
            self.max_queue_history.append(max_q)
            if max_q > self.l_max and len(all_c) < self.N:
                if self.add_reserve(t):
                    self.redistribute()
                    if self.reserve_cashiers and self.reserve_cashiers[-1].queue:
                        service_end[self.reserve_cashiers[-1].id] = t + random.randint(1, self.t2)
            self.process_breaks(t)
        return self.get_stats()
    
    def get_stats(self):
        all_c = self.cashiers + self.reserve_cashiers
        total = sum(c.total_served for c in all_c)
        avg = sum(self.max_queue_history)/len(self.max_queue_history) if self.max_queue_history else 0
        return {'regular': len(self.cashiers), 'reserve': len(self.reserve_cashiers), 'total_served': total, 'avg_queue': avg, 'max_queue': max(self.max_queue_history) if self.max_queue_history else 0}

if __name__ == "__main__":
    sim = SupermarketSimulation(10, 3, 10, 5, 8, 50, 10, 5, 10000)
    stats = sim.run()
    print("=== РЕЗУЛЬТАТИ ===")
    print(f"Звичайних: {stats['regular']}, Резервних: {stats['reserve']}")
    print(f"Обслуговано: {stats['total_served']}")
    print(f"Середня черга: {stats['avg_queue']:.2f}")
    print(f"Макс. черга: {stats['max_queue']}")
    plt.plot(sim.max_queue_history)
    plt.axhline(y=5, color='r', linestyle='--')
    plt.show()
