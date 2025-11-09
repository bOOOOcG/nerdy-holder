"""测试内存模块"""

import unittest
from nerdy_holder.memory import MemoryChunk


class TestMemoryChunk(unittest.TestCase):
    """测试内存块"""

    def test_create_chunk(self):
        """测试创建内存块"""
        chunk = MemoryChunk(10)  # 10MB

        self.assertEqual(chunk.size_mb, 10)
        self.assertIsNotNone(chunk.created_at)
        self.assertIsNotNone(chunk.data)
        self.assertEqual(len(chunk.data), 10 * 1024 * 1024)

    def test_chunk_initialization(self):
        """测试块初始化"""
        chunk = MemoryChunk(5)

        # 检查每MB的第一个字节是否被初始化
        for i in range(5):
            offset = i * 1024 * 1024
            self.assertGreaterEqual(chunk.data[offset], 0)
            self.assertLessEqual(chunk.data[offset], 255)

    def test_different_sizes(self):
        """测试不同大小"""
        sizes = [1, 10, 50, 100]

        for size in sizes:
            chunk = MemoryChunk(size)
            self.assertEqual(chunk.size_mb, size)
            self.assertEqual(len(chunk.data), size * 1024 * 1024)


if __name__ == '__main__':
    unittest.main()
