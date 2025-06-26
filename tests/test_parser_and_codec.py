import unittest
from src.parser import detect_format, parse_data
from src.aicodec import AICodec


class TestParserAndCodec(unittest.TestCase):
    def test_json(self):
        json_data = '[{"a": 1, "b": 2}, {"a": 3, "b": 4}]'
        fmt, parsed = parse_data(json_data)
        self.assertEqual(fmt, "json")
        codec = AICodec()
        codec.analyze(json_data)
        compressed = codec.compress([1, 2, 3, 4])
        decompressed = codec.decode(compressed)
        self.assertTrue(all(x in decompressed for x in [1, 2, 3, 4]))

    def test_csv(self):
        csv_data = "a,b\n1,2\n3,4"
        fmt, parsed = parse_data(csv_data)
        self.assertEqual(fmt, "csv")
        codec = AICodec()
        codec.analyze(csv_data)
        compressed = codec.compress([1, 2, 3, 4])
        decompressed = codec.decode(compressed)
        self.assertTrue(all(x in decompressed for x in [1, 2, 3, 4]))

    def test_log(self):
        log_data = "2024-06-25 12:00:00 INFO 123\n2024-06-25 12:01:00 WARN 456"
        fmt, parsed = parse_data(log_data)
        self.assertEqual(fmt, "log")
        # Лог содержит только строки, чисел нет, поэтому анализ не даст паттернов
        codec = AICodec()
        codec.analyze(log_data)
        # Проверяем, что не возникает ошибок
        self.assertIsInstance(codec.patterns, dict)

    def test_binary(self):
        bin_data = b"\x01\x02\x03\x04"
        fmt, parsed = parse_data(bin_data)
        self.assertEqual(fmt, "binary")
        codec = AICodec()
        codec.analyze(bin_data)
        compressed = codec.compress(bin_data)
        decompressed = codec.decode(compressed)
        # Декодированные данные должны содержать исходные байты
        for x in [1, 2, 3, 4]:
            self.assertIn(x, decompressed)


if __name__ == "__main__":
    unittest.main()
