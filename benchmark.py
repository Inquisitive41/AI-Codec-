import time
import gzip
import lz4.frame as lz4f
import pickle
import psutil
import os
import asyncio
from src.aicodec import AICodec

csv_path = "tests/test.csv"


# Utility: measure memory usage
def memory_usage_mb():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024


# Read data
with open(csv_path, "r", encoding="utf-8") as f:
    lines = f.readlines()
    data = []
    for line in lines[1:10001]:  # 10k строк для скорости
        data.extend([int(x) for x in line.strip().split(",") if x.isdigit()])


# AI-Codec benchmark
async def benchmark_aicodec(data):
    ai = AICodec(window=5)
    mem_before = memory_usage_mb()
    t0 = time.time()
    await ai.analyze(data)
    compressed = await ai.compress(data)
    t1 = time.time()
    decompressed = ai.decode(compressed)
    t2 = time.time()
    mem_after = memory_usage_mb()
    comp_ratio = (
        (len(pickle.dumps(data)) - len(pickle.dumps(compressed)))
        / len(pickle.dumps(data))
        * 100
    )
    return {
        "compress_time_ms": (t1 - t0) * 1000,
        "decompress_time_ms": (t2 - t1) * 1000,
        "compression_ratio_percent": comp_ratio,
        "memory_mb": mem_after - mem_before,
    }


# Gzip benchmark
def benchmark_gzip(data):
    mem_before = memory_usage_mb()
    t0 = time.time()
    compressed = gzip.compress(pickle.dumps(data))
    t1 = time.time()
    decompressed = pickle.loads(gzip.decompress(compressed))
    t2 = time.time()
    mem_after = memory_usage_mb()
    comp_ratio = (
        (len(pickle.dumps(data)) - len(compressed)) / len(pickle.dumps(data)) * 100
    )
    return {
        "compress_time_ms": (t1 - t0) * 1000,
        "decompress_time_ms": (t2 - t1) * 1000,
        "compression_ratio_percent": comp_ratio,
        "memory_mb": mem_after - mem_before,
    }


# LZ4 benchmark
def benchmark_lz4(data):
    mem_before = memory_usage_mb()
    t0 = time.time()
    compressed = lz4f.compress(pickle.dumps(data))
    t1 = time.time()
    decompressed = pickle.loads(lz4f.decompress(compressed))
    t2 = time.time()
    mem_after = memory_usage_mb()
    comp_ratio = (
        (len(pickle.dumps(data)) - len(compressed)) / len(pickle.dumps(data)) * 100
    )
    return {
        "compress_time_ms": (t1 - t0) * 1000,
        "decompress_time_ms": (t2 - t1) * 1000,
        "compression_ratio_percent": comp_ratio,
        "memory_mb": mem_after - mem_before,
    }


async def main():
    print("AI-Codec...")
    ai_metrics = await benchmark_aicodec(data)
    print("Gzip...")
    gzip_metrics = benchmark_gzip(data)
    print("LZ4...")
    lz4_metrics = benchmark_lz4(data)
    print("\nRESULTS:")
    print("AI-Codec:", ai_metrics)
    print("Gzip   :", gzip_metrics)
    print("LZ4    :", lz4_metrics)


if __name__ == "__main__":
    asyncio.run(main())
