"""内存分配器"""

import random
import threading


class MemoryAllocator:
    """智能内存分配器"""

    def __init__(self):
        self.chunks = []
        self.lock = threading.Lock()

    def allocate_mb(self, mb):
        """分配指定MB"""
        with self.lock:
            try:
                chunk = bytearray(int(mb * 1024 * 1024))
                for i in range(0, len(chunk), 1024*1024):
                    chunk[i] = random.randint(0, 255)
                self.chunks.append(chunk)
                return mb
            except Exception:
                return 0

    def release_mb(self, mb):
        """释放指定MB"""
        with self.lock:
            released = 0
            while self.chunks and released < mb:
                chunk = self.chunks.pop()
                released += len(chunk) / (1024*1024)
            return released

    def release_all(self):
        """释放全部"""
        with self.lock:
            total = sum(len(c) for c in self.chunks) / (1024*1024)
            self.chunks.clear()
            return total

    def get_total_mb(self):
        """获取总持有量"""
        with self.lock:
            return sum(len(c) for c in self.chunks) / (1024*1024)
