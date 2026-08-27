import re
from dataclasses import dataclass


BANNED_TERMS = [
    "更深层次的技术突破",
    "成为主流",
    "重大进展",
    "取得更多突破",
    "一定会给 AI 带来重大突破",
    "将成为研究的重点",
]


@dataclass
class ValidationItem:
    name: str
    passed: bool
    detail: str


def validate_final_output(raw_output) -> str:
    text = str(raw_output)
    final_version = _extract_between(
        text,
        start_marker="最终优化版本：",
        end_markers=["审稿意见：", "审稿意见:"],
    )
    review_notes = _extract_after_any(text, ["审稿意见：", "审稿意见:"])

    items = [
        _validate_final_version_exists(final_version),
        _validate_character_count(final_version),
        _validate_paragraph_count(final_version),
        _validate_banned_terms(final_version),
        _validate_review_notes_exist(review_notes),
        _validate_review_notes_applied(final_version, review_notes),
    ]

    lines = ["后处理校验报告:"]
    for item in items:
        status = "PASS" if item.passed else "FAIL"
        lines.append(f"- [{status}] {item.name}: {item.detail}")
    return "\n".join(lines)


def _extract_between(text: str, start_marker: str, end_markers: list[str]) -> str:
    start = text.find(start_marker)
    if start == -1:
        return ""

    start += len(start_marker)
    end_candidates = [
        text.find(marker, start) for marker in end_markers if text.find(marker, start) != -1
    ]
    end = min(end_candidates) if end_candidates else len(text)
    return text[start:end].strip()


def _extract_after_any(text: str, markers: list[str]) -> str:
    indexes = [(text.find(marker), marker) for marker in markers if text.find(marker) != -1]
    if not indexes:
        return ""
    start, marker = min(indexes, key=lambda item: item[0])
    return text[start + len(marker) :].strip()


def _validate_final_version_exists(final_version: str) -> ValidationItem:
    return ValidationItem(
        name="最终优化版本存在",
        passed=bool(final_version),
        detail="已找到最终优化版本。" if final_version else "没有找到“最终优化版本：”。",
    )


def _validate_character_count(final_version: str) -> ValidationItem:
    count = len(re.findall(r"[\u4e00-\u9fff]", final_version))
    passed = 180 <= count <= 220
    return ValidationItem(
        name="中文字数 180-220",
        passed=passed,
        detail=f"当前中文字数={count}。",
    )


def _validate_paragraph_count(final_version: str) -> ValidationItem:
    paragraphs = [p for p in re.split(r"\n\s*\n", final_version.strip()) if p.strip()]
    passed = len(paragraphs) == 3
    return ValidationItem(
        name="最终版本分为 3 段",
        passed=passed,
        detail=f"当前段落数={len(paragraphs)}。",
    )


def _validate_banned_terms(final_version: str) -> ValidationItem:
    found = [term for term in BANNED_TERMS if term in final_version]
    return ValidationItem(
        name="禁用/过强表达检查",
        passed=not found,
        detail="未发现禁用表达。" if not found else f"仍包含: {', '.join(found)}。",
    )


def _validate_review_notes_exist(review_notes: str) -> ValidationItem:
    return ValidationItem(
        name="审稿意见存在",
        passed=bool(review_notes),
        detail="已找到审稿意见。" if review_notes else "没有找到“审稿意见：”。",
    )


def _validate_review_notes_applied(final_version: str, review_notes: str) -> ValidationItem:
    failures = []

    for old, new in re.findall(r"将“([^”]+)”改为“([^”]+)”", review_notes):
        if old in final_version:
            failures.append(f"仍保留待替换表达“{old}”")
        if new not in final_version:
            failures.append(f"未落实替换结果“{new}”")

    for deleted in re.findall(r"删除“([^”]+)”", review_notes):
        if deleted in final_version:
            failures.append(f"仍保留应删除内容“{deleted}”")

    if not review_notes:
        return ValidationItem(
            name="审稿意见落实检查",
            passed=False,
            detail="缺少审稿意见，无法校验是否落实。",
        )

    if not re.search(r"将“[^”]+”改为“[^”]+”|删除“[^”]+”", review_notes):
        return ValidationItem(
            name="审稿意见落实检查",
            passed=True,
            detail="审稿意见没有明确的“改为/删除”指令。",
        )

    return ValidationItem(
        name="审稿意见落实检查",
        passed=not failures,
        detail="明确修改意见均已落实。" if not failures else "；".join(failures),
    )

