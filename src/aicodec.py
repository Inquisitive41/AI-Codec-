import numpy as np
from collections import defaultdict
import hashlib

class AICodec:
    def __init__(self, window=3):
        """
        Инициализация кодека.
        :param window: Размер окна для анализа паттернов (по умолчанию 3).
        """
        self.patterns = defaultdict(int)  # Хранит частоту последовательностей
        self.freq = defaultdict(int)      # Хранит частоту следующего значения
        self.window = window              # Размер окна
        self.fractal_depth = lambda i: 1 + np.log2(i + 1)  # Фрактальный коэффициент

    def analyze(self, data):
        """
        Анализирует данные для построения статистик паттернов.
        :param data: Список чисел или байты, представляющие данные.
        """
        if isinstance(data, bytes):
            data_int = [int.from_bytes(data[i:i+1], 'big') for i in range(0, len(data), 1)]
        else:
            data_int = data

        for i in range(len(data_int) - 1):
            seq = tuple(data_int[i:i + self.window])
            self.patterns[seq] += 1
            if i + self.window < len(data_int):
                self.freq[data_int[i + self.window]] += 1

    def fractal_entropy(self, seq):
        """
        Вычисляет энтропию для фрактальных паттернов.
        :param seq: Последовательность для анализа.
        :return: Энтропия в битах.
        """
        entropy = 0
        for i in range(len(seq)):
            sub_seq = seq[:i + 1]
            prob = self.patterns[sub_seq] / sum(self.patterns.values()) if sub_seq in self.patterns else 0.5
            if prob > 0:
                entropy += prob * np.log2(1 / prob) * self.fractal_depth(i)
        return entropy

    def compress(self, data):
        """
        Сжимает данные в формате кортежей (последовательность, вероятность, следующее значение, энтропия).
        :param data: Список чисел или байты.
        :return: Список сжатых данных.
        """
        if isinstance(data, bytes):
            data_int = [int.from_bytes(data[i:i+1], 'big') for i in range(0, len(data), 1)]
        else:
            data_int = data

        compressed = []
        for i in range(len(data_int) - self.window + 1):
            seq = tuple(data_int[i:i + self.window])
            next_val = data_int[i + self.window] if i + self.window < len(data_int) else None
            prob = self.patterns[seq] / self.freq[data_int[i]] if seq in self.patterns and data_int[i] in self.freq else 0.5
            entropy = self.fractal_entropy(seq)
            compressed.append((seq, prob, next_val, entropy))
        return compressed

    def decode(self, compressed):
        """
        Восстанавливает оригинальные данные из сжатого формата.
        :param compressed: Список кортежей от compress.
        :return: Восстановленный список данных.
        """
        decoded = []
        for seq, _, next_val, _ in compressed:
            if next_val is not None:
                decoded.extend(list(seq)[1:] + [next_val])  # Сдвигаем окно и добавляем следующее значение
            else:
                decoded.extend(list(seq)[1:])  # Для последнего фрагмента
        return decoded

    def save_compressed(self, compressed, filename):
        """
        Сохраняет сжатые данные в бинарный файл.
        :param compressed: Список сжатых данных.
        :param filename: Имя файла для сохранения.
        """
        with open(filename, "wb") as f:
            for item in compressed:
                f.write(str(item).encode() + b"\n")

    def load_compressed(self, filename):
        """
        Загружает сжатые данные из бинарного файла.
        :param filename: Имя файла для чтения.
        :return: Список сжатых данных.
        """
        with open(filename, "rb") as f:
            return [eval(line.decode()) for line in f]

    def verify_integrity(self, original, decompressed):
        """
        Проверяет целостность данных с помощью хеша MD5.
        :param original: Оригинальные данные.
        :param decompressed: Разжатые данные.
        :return: Сообщение о результате.
        """
        orig_hash = hashlib.md5(str(original).encode()).hexdigest()
        decomp_hash = hashlib.md5(str(decompressed).encode()).hexdigest()
        return f"Хеши совпадают: {orig_hash == decomp_hash} (Оригинал: {orig_hash}, Разжатое: {decomp_hash})"

# Пример использования
if __name__ == "__main__":
    # Тестовые данные: временной ряд (квадраты чисел)
    test_data = [1, 4, 9, 16, 25]
    byte_data = b''.join([str(x).encode() + b',' for x in test_data])[:-1]  # Пример с байтами

    # Инициализация кодека
    codec = AICodec(window=2)  # Уменьшаем окно для простоты теста

    # Анализ данных (обязательно перед сжатием)
    codec.analyze(test_data)
    # или для байтов
    # codec.analyze(byte_data)

    # Сжатие
    compressed = codec.compress(test_data)
    # или для байтов
    # compressed = codec.compress(byte_data)
    print("Сжатые данные:", compressed)

    # Сохранение в файл (опционально)
    codec.save_compressed(compressed, "compressed.bin")

    # Загрузка из файла (опционально)
    loaded_compressed = codec.load_compressed("compressed.bin")

    # Разжатие
    decompressed = codec.decode(compressed)
    print("Разжатые данные:", decompressed)

    # Проверка целостности
    integrity_check = codec.verify_integrity(test_data, decompressed)
    print(integrity_check)

    # Тест с байтами
    codec_byte = AICodec(window=2)
    codec_byte.analyze(byte_data)
    compressed_byte = codec_byte.compress(byte_data)
    decompressed_byte = codec_byte.decode(compressed_byte)
    byte_data_list = [int.from_bytes(byte_data[i:i+1], 'big') for i in range(0, len(byte_data), 1)]
    decompressed_byte_list = decompressed_byte
    integrity_check_byte = codec_byte.verify_integrity(byte_data_list, decompressed_byte_list)
    print("Целостность для байтов:", integrity_check_byte)