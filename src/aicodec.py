import numpy as np
from collections import defaultdict
import hashlib
import logging
import json
import pandas as pd
import re
import asyncio
from arithmeticcoding import ArithmeticCoder
import heapq
import ast
import jinja2
import time
import os
from typing import List, Tuple, Union, Generator
import matplotlib.pyplot as plt
import boto3
from azure.storage.blob import BlobServiceClient
from google.cloud import storage

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AICodec:
    """
    AI-Codec: Advanced context-aware compression and analysis algorithm with FSM, hybrid coding, async streaming, and cloud support.
    """

    # Состояния FSM
    INIT, ANALYZE, COMPRESS, PREDICT = range(4)

    def __init__(self, window=3, buffer_size=100, threshold_ms=50):
        """
        Initialize the AI-Codec instance.

        Args:
            window (int): Window size for pattern analysis.
            buffer_size (int): Buffer size for streaming.
            threshold_ms (int): Max allowed processing delay in ms.
        """
        self.patterns = defaultdict(int)
        self.freq = defaultdict(int)
        self.window = window
        self.buffer_size = buffer_size
        self.threshold_ms = threshold_ms
        self.state = self.INIT
        self.buffer = []
        self.fsm_states = {}
        self.huffman_codes = {}
        self.arith_coder = ArithmeticCoder()

    def _detect_format(self, data: Union[str, bytes, List]) -> str:
        """
        Detects the format of the input data (json, csv, log, binary, unknown).

        Args:
            data (str|bytes|list): Input data.
        Returns:
            str: Detected format.
        """
        if isinstance(data, str):
            if data.strip().startswith("{") or data.strip().startswith("["):
                return "json"
            elif "," in data and not "{" in data:
                return "csv"
            elif re.search(r"\d{4}-\d{2}-\d{2}", data):
                return "log"
        elif isinstance(data, bytes):
            return "binary"
        return "unknown"

    def _parse_data(self, data: Union[str, bytes, List]) -> List:
        """
        Parses input data to a list of integers for analysis/compression.

        Args:
            data (str|bytes|list): Input data.
        Returns:
            list: Parsed integer data.
        """
        fmt = self._detect_format(data)
        if fmt == "json":
            return [
                int(v) for v in json.loads(data).values() if isinstance(v, (int, float))
            ]
        elif fmt == "csv":
            df = pd.read_csv(pd.StringIO(data))
            return df.values.flatten().astype(int).tolist()
        elif fmt == "log":
            return [int(m.group(0)) for m in re.finditer(r"\d+", data)]
        elif fmt == "binary":
            return [
                int.from_bytes(data[i : i + 1], "big") for i in range(0, len(data), 1)
            ]
        return data if isinstance(data, list) else []

    async def _process_chunk_async(self, chunk: Union[List, bytes]):
        """
        Asynchronously processes a chunk of data and updates the buffer.

        Args:
            chunk (list|bytes): Data chunk.
        """
        parsed = self._parse_data(chunk)
        self.buffer.extend(parsed)
        if len(self.buffer) > self.buffer_size:
            self.buffer = self.buffer[-self.buffer_size :]
        await asyncio.sleep(0)  # Асинхронная пауза

    def _build_fsm(self):
        """
        Builds the FSM state transition table from patterns.
        """
        for seq in self.patterns:
            state = hash(seq)
            for i, sym in enumerate(seq):
                next_state = hash(seq[: i + 1]) if i < len(seq) - 1 else None
                self.fsm_states[(state, sym)] = next_state
                if next_state:
                    self.fsm_states[(state, sym)] = next_state

    def _build_huffman(self):
        """
        Builds Huffman codes for lossless part of the data.
        """
        heap = [[weight, [symbol, ""]] for symbol, weight in self.freq.items()]
        heapq.heapify(heap)
        while len(heap) > 1:
            lo = heapq.heappop(heap)
            hi = heapq.heappop(heap)
            for pair in lo[1:]:
                pair[1] = "0" + pair[1]
            for pair in hi[1:]:
                pair[1] = "1" + pair[1]
            heapq.heappush(heap, [lo[0] + hi[0]] + lo[1:] + hi[1:])
        self.huffman_codes = dict(heapq.heappop(heap)[1:])

    async def analyze(self, data: Union[List, bytes, Generator]) -> None:
        """
        Asynchronously analyzes data, builds patterns and frequency tables.

        Args:
            data (list|bytes|generator): Input data or data stream.
        """
        self.state = self.ANALYZE
        self.buffer = []
        if isinstance(data, Generator):
            await asyncio.gather(*(self._process_chunk_async(chunk) for chunk in data))
        else:
            await self._process_chunk_async(data)
        self._build_fsm()
        for i in range(len(self.buffer) - self.window + 1):
            seq = tuple(self.buffer[i : i + self.window])
            self.patterns[seq] += 1
            if i + self.window < len(self.buffer):
                self.freq[self.buffer[i + self.window]] += 1
        logger.info(f"Анализ завершён. Паттернов: {len(self.patterns)}")

    def fractal_entropy(self, seq: Tuple) -> float:
        """
        Calculates fractal entropy for a given sequence.

        Args:
            seq (tuple): Sequence of values.
        Returns:
            float: Fractal entropy value.
        """
        entropy = 0
        total = sum(self.patterns.values())
        for i in range(len(seq)):
            sub_seq = seq[: i + 1]
            prob = (
                self.patterns[sub_seq] / total
                if sub_seq in self.patterns and total > 0
                else 0.01
            )
            if prob > 0:
                entropy += prob * np.log2(1 / prob) * (1 + np.log2(i + 1))
        return entropy

    async def compress(self, data: Union[List, bytes, Generator]) -> List[Tuple]:
        """
        Asynchronously compresses data using hybrid coding (Huffman/Arithmetic).

        Args:
            data (list|bytes|generator): Input data or data stream.
        Returns:
            list: List of compressed tuples.
        """
        self.state = self.COMPRESS
        self._build_huffman()
        start_time = time.time()
        if isinstance(data, Generator):
            compressed = []
            async for chunk in self._stream_data(data):
                chunk_comp = await self._compress_chunk(chunk)
                compressed.extend(chunk_comp)
            delay = (time.time() - start_time) * 1000
            if delay > self.threshold_ms:
                logger.warning(
                    f"Задержка: {delay:.2f} мс превышает порог {self.threshold_ms} мс"
                )
            return compressed
        else:
            compressed = await self._compress_chunk(data)
            delay = (time.time() - start_time) * 1000
            if delay > self.threshold_ms:
                logger.warning(
                    f"Задержка: {delay:.2f} мс превышает порог {self.threshold_ms} мс"
                )
            return compressed

    async def _stream_data(self, data: Generator) -> Generator:
        """
        Asynchronously yields chunks from a data generator.

        Args:
            data (generator): Data generator.
        Yields:
            chunk: Next chunk of data.
        """
        async for chunk in data:
            yield chunk

    async def _compress_chunk(self, data: Union[List, bytes]) -> List[Tuple]:
        """
        Asynchronously compresses a chunk of data.

        Args:
            data (list|bytes): Data chunk.
        Returns:
            list: List of compressed tuples.
        """
        data_int = self._parse_data(data)
        compressed = []
        for i in range(len(data_int) - self.window + 1):
            seq = tuple(data_int[i : i + self.window])
            next_val = (
                data_int[i + self.window] if i + self.window < len(data_int) else None
            )
            prob = (
                self.patterns[seq] / sum(self.freq.values())
                if seq in self.patterns and sum(self.freq.values()) > 0
                else 0.5
            )
            entropy = self.fractal_entropy(seq)
            coding_method = "huffman" if prob > 0.1 else "arithmetic"
            code = (
                self.huffman_codes.get(next_val, "0" * 8)
                if coding_method == "huffman"
                else self.arith_coder.encode(prob, next_val)
            )
            pred_prob = {
                val: (self.freq[val] / sum(self.freq.values())) * np.exp(-entropy / 2)
                for val in self.freq
            }
            next_pred = (
                max(pred_prob, key=pred_prob.get) if next_val is None else next_val
            )
            compressed.append((seq, prob, next_pred, entropy, code, coding_method))
        return compressed

    def decode(self, compressed: List[Tuple]) -> List:
        """
        Decodes compressed data back to the original sequence.

        Args:
            compressed (list): List of compressed tuples.
        Returns:
            list: Decoded data.
        """
        if not compressed:
            return []
        decoded = list(compressed[0][0])
        for seq, _, next_val, _, code, method in compressed:
            if next_val is not None:
                decoded.append(
                    int(code, 2)
                    if method == "huffman"
                    else self.arith_coder.decode(code)
                )
        return decoded

    def benchmark(self, data: Union[List, bytes], iterations=10) -> dict:
        """
        Benchmarks AI-Codec, gzip, and lz4 on the given data.

        Args:
            data (list|bytes): Input data.
            iterations (int): Number of iterations for averaging.
        Returns:
            dict: Benchmark results for all codecs.
        """
        import gzip
        import lz4.frame as lz4f

        results = {"aicodec": {}, "gzip": {}, "lz4": {}}
        # AICodec
        start_mem = memory_usage()
        start_time = time.time()
        for _ in range(iterations):
            compressed = self.compress(data)
            decompressed = self.decode(compressed)
        comp_time = (time.time() - start_time) / iterations * 1000
        comp_ratio = (len(str(data)) - len(str(compressed))) / len(str(data)) * 100
        mem_usage = memory_usage() - start_mem
        results["aicodec"] = {
            "compression_time_ms": comp_time,
            "compression_ratio_percent": comp_ratio,
            "memory_mb": mem_usage,
        }
        # Gzip
        start_time = time.time()
        for _ in range(iterations):
            compressed = gzip.compress(str(data).encode())
            decompressed = gzip.decompress(compressed).decode()
        comp_time = (time.time() - start_time) / iterations * 1000
        comp_ratio = (
            (len(str(data).encode()) - len(compressed)) / len(str(data).encode()) * 100
        )
        results["gzip"] = {
            "compression_time_ms": comp_time,
            "compression_ratio_percent": comp_ratio,
        }
        # LZ4
        start_time = time.time()
        for _ in range(iterations):
            compressed = lz4f.compress(str(data).encode())
            decompressed = lz4f.decompress(compressed).decode()
        comp_time = (time.time() - start_time) / iterations * 1000
        comp_ratio = (
            (len(str(data).encode()) - len(compressed)) / len(str(data).encode()) * 100
        )
        results["lz4"] = {
            "compression_time_ms": comp_time,
            "compression_ratio_percent": comp_ratio,
        }
        return results

    def generate_readme(self):
        """
        Autogenerates README.md using AST and Jinja2 templates.
        """
        tree = ast.parse(open(__file__).read())
        functions = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)
        ]
        classes = [
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        ]
        template = jinja2.Template(
            """
# AICodec

## Описание
Алгоритм сжатия и анализа данных с поддержкой FSM и гибридного кодирования.

## Функции
{% for func in functions %}
- `{{ func }}`
{% endfor %}

## Классы
{% for cls in classes %}
- `{{ cls }}`
{% endfor %}

## Установка
```bash
pip install aicodec         
"""
        )
        print(template.render(functions=functions, classes=classes))


# Пример использования
if __name__ == "__main__":
    # Тестовые данные
    test_data = [1, 4, 9, 16, 25, 36]
    byte_data = b"".join([str(x).encode() + b"," for x in test_data])[:-1]
    text_data = "error log: 2025-06-27, success log: 2025-06-27"

    ai = AICodec(window=3, buffer_size=200, threshold_ms=50)

    async def main():
        async def data_stream():
            for i in range(0, len(test_data), 2):
                yield test_data[i : i + 2]

        await ai.analyze(data_stream())
        semantics = ai.semantic_analyze(text_data)
        print("Семантический анализ:", semantics)
        compressed = await ai.compress(data_stream())
        print("Сжатые данные:", compressed[:5])
        prob, next_val = ai.predict(tuple(test_data[-2:]))
        print(f"Предсказание следующего: {next_val} (вероятность: {prob:.2f})")
        decompressed = ai.decode(compressed)
        print("Разжатые данные:", decompressed)
        ai.visualize(test_data, compressed)
        metrics = ai.measure_performance(test_data)
        print("Производительность:", metrics)

    import asyncio

    asyncio.run(main())
