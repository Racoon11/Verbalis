from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
import re

import requests


@dataclass
class GrammarError:
    offset: int
    length: int
    bad_text: str
    message: str
    replacements: list[str]
    rule_id: str
    category: str


@dataclass
class CheckResult:
    sentence: str
    word: str
    word_found: bool
    is_correct: bool
    errors: list[GrammarError] = field(default_factory=list)
    corrected_sentence: Optional[str] = None


class SentenceChecker:
    _DEFAULT_API = "https://api.languagetool.org/v2/check"

    def __init__(self, language: str = "en-US", base_url: str = _DEFAULT_API) -> None:
        self.language = language
        self.base_url = base_url
        self._session = requests.Session()

    def check(self, word: str, sentence: str) -> CheckResult:
        word_found = bool(re.search(rf"\b{re.escape(word)}\b", sentence, re.IGNORECASE))
        matches = self._fetch_matches(sentence)
        errors = [_match_to_error(sentence, m) for m in matches]
        corrected = _apply_corrections(sentence, errors) if errors else None
        return CheckResult(
            sentence=sentence,
            word=word,
            word_found=word_found,
            is_correct=len(errors) == 0,
            errors=errors,
            corrected_sentence=corrected,
        )

    def close(self) -> None:
        self._session.close()

    def __enter__(self) -> "SentenceChecker":
        return self

    def __exit__(self, *_) -> None:
        self.close()

    def _fetch_matches(self, text: str) -> list[dict]:
        response = self._session.post(
            self.base_url,
            data={"text": text, "language": self.language},
            timeout=10,
        )
        response.raise_for_status()
        return response.json().get("matches", [])


def _match_to_error(sentence: str, match: dict) -> GrammarError:
    offset = match["offset"]
    length = match["length"]
    return GrammarError(
        offset=offset,
        length=length,
        bad_text=sentence[offset: offset + length],
        message=match["message"],
        replacements=[r["value"] for r in match["replacements"][:3]],
        rule_id=match["rule"]["id"],
        category=match["rule"]["category"]["id"],
    )


def _apply_corrections(sentence: str, errors: list[GrammarError]) -> str:
    result = sentence
    shift = 0
    for error in sorted(errors, key=lambda e: e.offset):
        if not error.replacements:
            continue
        start = error.offset + shift
        end = start + error.length
        replacement = error.replacements[0]
        result = result[:start] + replacement + result[end:]
        shift += len(replacement) - error.length
    return result
