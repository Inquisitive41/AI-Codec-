import unittest
import numpy as np
from src.aicodec import AICodec


class TestAICodec(unittest.TestCase):
    def setUp(self):
        self.codec = AICodec(auto_parse=False)
        self.data = [1, 4, 9, 16, 25]

    def test_analyze(self):
        self.codec.analyze(self.data)
        self.assertTrue(len(self.codec.patterns) > 0)

    def test_compress_and_decode(self):
        self.codec.analyze(self.data)
        compressed = self.codec.compress(self.data)
        self.assertTrue(len(compressed) > 0)
        decoded = self.codec.decode(compressed)
        # Проверяем, что декодированные данные содержат исходные элементы
        for val in self.data:
            self.assertIn(val, decoded)


if __name__ == "__main__":
    unittest.main()
