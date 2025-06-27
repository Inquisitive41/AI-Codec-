from src.aicodec import HyperStream
import pickle

csv_path = "tests/test.csv"
block_size = 100_000
raw_total = 0
comp_total = 0
block_num = 0


def parse_line(line):
    return [int(x) for x in line.strip().split(",") if x.isdigit()]


with open(csv_path, "r", encoding="utf-8") as f:
    header = next(f)
    block = []
    for line in f:
        block.extend(parse_line(line))
        if len(block) >= block_size:
            hs = HyperStream(dynamic_window=True)
            hs.analyze(block)
            compressed = hs.compress(block)
            raw_bytes = pickle.dumps(block)
            comp_bytes = pickle.dumps(compressed)
            raw_total += len(raw_bytes)
            comp_total += len(comp_bytes)
            block_num += 1
            print(
                f"Block {block_num}: Raw {len(raw_bytes)} bytes, Compressed {len(comp_bytes)} bytes, Ratio {len(comp_bytes)/len(raw_bytes):.2f}"
            )
            block = []
    # Последний блок
    if block:
        hs = HyperStream(dynamic_window=True)
        hs.analyze(block)
        compressed = hs.compress(block)
        raw_bytes = pickle.dumps(block)
        comp_bytes = pickle.dumps(compressed)
        raw_total += len(raw_bytes)
        comp_total += len(comp_bytes)
        block_num += 1
        print(
            f"Block {block_num}: Raw {len(raw_bytes)} bytes, Compressed {len(comp_bytes)} bytes, Ratio {len(comp_bytes)/len(raw_bytes):.2f}"
        )

print(
    f"\nTOTAL: Raw {raw_total} bytes, Compressed {comp_total} bytes, Ratio {comp_total/raw_total:.2f}"
)
