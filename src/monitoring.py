import os
import time
from functools import wraps

import psutil


class ResourceMonitor:
    def __init__(self) -> None:
        self.process = psutil.Process(os.getpid())
        psutil.cpu_percent(interval=None)
        self.process.cpu_percent(interval=None)

    def snapshot(self) -> str:
        system_memory = psutil.virtual_memory()
        python_memory_mb = self.process.memory_info().rss / 1024 / 1024
        python_cpu = self.process.cpu_percent(interval=None)
        system_cpu = psutil.cpu_percent(interval=None)
        ollama_memory_mb = self._ollama_memory_mb()

        return (
            f"system_cpu={system_cpu:.1f}% | "
            f"system_ram={system_memory.percent:.1f}% "
            f"({system_memory.used / 1024 / 1024 / 1024:.1f}GB/"
            f"{system_memory.total / 1024 / 1024 / 1024:.1f}GB) | "
            f"python_cpu={python_cpu:.1f}% | "
            f"python_ram={python_memory_mb:.1f}MB | "
            f"ollama_ram={ollama_memory_mb:.1f}MB"
        )

    def _ollama_memory_mb(self) -> float:
        total = 0.0
        for proc in psutil.process_iter(["name", "memory_info"]):
            try:
                name = (proc.info["name"] or "").lower()
                if "ollama" in name:
                    total += proc.info["memory_info"].rss / 1024 / 1024
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return total


class LLMCallStats:
    def __init__(self) -> None:
        self.records = []

    def add(self, call_id: int, label: str, duration_seconds: float) -> None:
        self.records.append(
            {
                "call_id": call_id,
                "label": label,
                "duration_seconds": duration_seconds,
            }
        )

    def format_summary(self) -> str:
        if not self.records:
            return "没有记录到 LLM 调用。"

        lines = ["LLM 调用时间汇总:"]
        total = 0.0
        for record in self.records:
            duration = record["duration_seconds"]
            total += duration
            lines.append(
                f"- {record['label']}: {duration:.2f}s "
                f"(LLM Call #{record['call_id']})"
            )
        lines.append(f"- 总 LLM 调用时间: {total:.2f}s")
        return "\n".join(lines)


def instrument_llm(llm, monitor: ResourceMonitor, labels=None):
    original_call = llm.call
    call_count = {"value": 0}
    stats = LLMCallStats()
    labels = labels or []

    @wraps(original_call)
    def timed_call(*args, **kwargs):
        call_count["value"] += 1
        call_id = call_count["value"]
        label = labels[call_id - 1] if call_id <= len(labels) else f"未知调用 {call_id}"
        started_at = time.perf_counter()

        print(f"\n[LLM Call #{call_id} | {label}] started | {monitor.snapshot()}")
        try:
            return original_call(*args, **kwargs)
        finally:
            elapsed = time.perf_counter() - started_at
            stats.add(call_id, label, elapsed)
            print(
                f"\n[LLM Call #{call_id} | {label}] finished | "
                f"duration={elapsed:.2f}s | {monitor.snapshot()}"
            )

    llm.call = timed_call
    return llm, stats
