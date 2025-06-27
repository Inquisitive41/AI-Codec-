# AI-Codec

AI-Codec — современный асинхронный алгоритм контекстно-зависимого сжатия и анализа структурированных данных с поддержкой FSM, гибридного кодирования (Huffman/Arithmetic), потоковой обработки, семантики, облака и автогенерации документации.

## Возможности
- Автоматическое определение формата (JSON, CSV, логи, бинарные данные)
- FSM и динамическое окно
- Гибридное кодирование (Huffman/Arithmetic)
- Асинхронная и потоковая обработка
- Буферизация и real-time
- Семантический анализ текста
- Сравнение с gzip/lz4
- Визуализация
- Облачные сервисы (AWS S3, Azure, Google Cloud)
- Автогенерация README

## Установка
```bash
pip install -r requirements.txt
```

## Пример использования
```python
import asyncio
from src.aicodec import AICodec

test_data = [1, 4, 9, 16, 25, 36]
ai = AICodec(window=3, buffer_size=200, threshold_ms=50)

async def main():
    async def data_stream():
        for i in range(0, len(test_data), 2):
            yield test_data[i:i+2]
    await ai.analyze(data_stream())
    compressed = await ai.compress(data_stream())
    decompressed = ai.decode(compressed)
    print("Сжатые данные:", compressed[:5])
    print("Разжатые данные:", decompressed)

asyncio.run(main())
```

## Зависимости
- numpy
- pandas
- matplotlib
- lz4
- boto3
- azure-storage-blob
- google-cloud-storage
- jinja2
- arithmeticcoding
- asyncio
- pytest
- pytest-asyncio

## Лицензия
MIT 