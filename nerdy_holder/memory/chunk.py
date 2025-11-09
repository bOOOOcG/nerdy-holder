"""内存块"""

import random
from datetime import datetime


class MemoryChunk:
    """内存块"""

    def __init__(self, size_mb):
        self.size_mb = size_mb
        self.created_at = datetime.now()
        self.data = bytearray(size_mb * 1024 * 1024)
        for i in range(0, len(self.data), 1024*1024):
            self.data[i] = random.randint(0, 255)
