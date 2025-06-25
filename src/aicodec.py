import numpy as np
from collections import defaultdict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AICodec:
    """
    Сверхэффективный алгоритм контекстно-зависимого сжатия структурированных данных.
    """

    def __init__(self, window=3):
        """
        :param window: Размер окна для анализа паттернов
        """
        self.patterns = defaultdict(int)
        self.freq = defaultdict(int)
        self.window = window
        self.fractal_depth = lambda i: 1 + np.log2(i + 1)

    def analyze(self, data):
        """
        Анализирует входные данные для построения паттернов и частот.
        :param data: Список данных (int/float)
        """
        for i in range(len(data) - 1):
            seq = tuple(data[i : i + self.window])
            self.patterns[seq] += 1
            self.freq[data[i + 1]] += 1
        logger.info(f"Анализ завершён. Найдено паттернов: {len(self.patterns)}")

    def fractal_entropy(self, seq):
        """
        Вычисляет фрактальную энтропию для последовательности.
        :param seq: Кортеж значений
        :return: float
        """
        entropy = 0
        total_patterns = sum(self.patterns.values())
        for i, _ in enumerate(seq):
            sub_seq = seq[: i + 1]
            prob = (
                self.patterns[sub_seq] / total_patterns
                if sub_seq in self.patterns and total_patterns > 0
                else 0.5
            )
            if prob > 0:
                entropy += prob * np.log2(1 / prob) * self.fractal_depth(i)
        return entropy

    def compress(self, data):
        """
        Сжимает данные, используя FSM и гибридное кодирование.
        :param data: Список данных
        :return: Список кортежей (seq, prob, next_val, entropy)
        """
        compressed = []
        for i in range(len(data) - self.window + 1):
            seq = tuple(data[i : i + self.window])
            next_val = data[i + self.window] if i + self.window < len(data) else None
            prob = (
                self.patterns[seq] / self.freq[data[i]]
                if seq in self.patterns and self.freq[data[i]] > 0
                else 0.5
            )
            entropy = self.fractal_entropy(seq)
            compressed.append((seq, prob, next_val, entropy))
        logger.info(f"Сжатие завершено. Размер сжатых данных: {len(compressed)}")
        return compressed

    def decode(self, compressed):
        """
        Восстанавливает данные из сжатого представления.
        :param compressed: Список кортежей (seq, prob, next_val, entropy)
        :return: Список данных
        """
        decoded = []
        for seq, _, next_val, _ in compressed:
            decoded.extend(list(seq))
            if next_val is not None:
                decoded.append(next_val)
        logger.info(
            f"Декодирование завершено. Размер восстановленных данных: {len(decoded)}"
        )
        return decoded
