import json
import csv
import re
from typing import Any, List, Dict, Tuple, Union


def detect_format(data: Union[str, bytes]) -> str:
    """
    Определяет формат входных данных: json, csv, log, binary.
    """
    if isinstance(data, bytes):
        try:
            data = data.decode()
        except Exception:
            return "binary"
    sample = data.strip()
    if sample.startswith("{") or sample.startswith("["):
        try:
            json.loads(sample)
            return "json"
        except Exception:
            pass
    if "," in sample or ";" in sample:
        try:
            csv.Sniffer().sniff(sample)
            return "csv"
        except Exception:
            pass
    if re.match(r"\d{4}-\d{2}-\d{2}.*", sample):
        return "log"
    return "binary"


def parse_json(data: str) -> List[Dict[str, Any]]:
    """
    Парсит JSON-строку в список словарей.
    """
    obj = json.loads(data)
    if isinstance(obj, dict):
        return [obj]
    if isinstance(obj, list):
        return obj
    return []


def parse_csv(data: str) -> List[Dict[str, Any]]:
    """
    Парсит CSV-строку в список словарей.
    """
    lines = data.strip().splitlines()
    reader = csv.DictReader(lines)
    return list(reader)


def parse_log(data: str) -> List[Dict[str, Any]]:
    """
    Примитивный парсер логов: разбивает строки на поля по пробелам.
    """
    lines = data.strip().splitlines()
    result = []
    for line in lines:
        parts = line.split()
        result.append({"raw": line, "fields": parts})
    return result


def parse_binary(data: bytes) -> List[int]:
    """
    Преобразует бинарные данные в список байтов (int).
    """
    return [b for b in data]


def parse_data(data: Union[str, bytes]) -> Tuple[str, Any]:
    """
    Автоматически определяет формат и парсит данные.
    :return: (detected_format, parsed_data)
    """
    fmt = detect_format(data)
    if fmt == "json":
        return fmt, parse_json(data.decode() if isinstance(data, bytes) else data)
    if fmt == "csv":
        return fmt, parse_csv(data.decode() if isinstance(data, bytes) else data)
    if fmt == "log":
        return fmt, parse_log(data.decode() if isinstance(data, bytes) else data)
    if fmt == "binary":
        return fmt, parse_binary(data if isinstance(data, bytes) else data.encode())
    return fmt, data
