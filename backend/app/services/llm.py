import json
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass
class LlmConfig:
    provider: str
    api_key: str
    base_url: str
    model: str
    timeout_seconds: int = 45


class RemoteLlmService:
    def __init__(self, config: LlmConfig | None) -> None:
        self._config = config

    @property
    def available(self) -> bool:
        return self._config is not None

    @property
    def provider(self) -> str | None:
        return self._config.provider if self._config else None

    def generate_answer(self, *, system_prompt: str, user_prompt: str) -> str:
        if self._config is None:
            raise RuntimeError("Remote LLM is not configured.")
        message = self._request_completion(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            max_tokens=700,
        )
        content = (message.get("content") or "").strip()
        if content:
            return content

        reasoning_content = (message.get("reasoning_content") or "").strip()
        if reasoning_content:
            summarized = self._summarize_reasoning(reasoning_content)
            if summarized:
                return summarized

        extracted = self._extract_answer_from_reasoning(reasoning_content)
        if extracted:
            return extracted
        raise RuntimeError("Remote LLM returned empty content.")

    def _request_completion(
        self,
        *,
        messages: list[dict[str, str]],
        max_tokens: int,
    ) -> dict[str, Any]:
        if self._config is None:
            raise RuntimeError("Remote LLM is not configured.")

        payload: dict[str, Any] = {
            "model": self._config.model,
            "messages": messages,
            "temperature": 0.2,
            "max_tokens": max_tokens,
        }

        request = Request(
            self._config.base_url.rstrip("/") + "/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {self._config.api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )

        try:
            with urlopen(request, timeout=self._config.timeout_seconds) as response:
                body = response.read().decode("utf-8")
        except HTTPError as exc:
            error_body = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"Remote LLM request failed with HTTP {exc.code}: {error_body}"
            ) from exc
        except URLError as exc:
            raise RuntimeError(f"Remote LLM request failed: {exc.reason}") from exc

        try:
            parsed = json.loads(body)
            return parsed["choices"][0]["message"]
        except (KeyError, IndexError, TypeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"Unexpected remote LLM response: {body}") from exc

    def _summarize_reasoning(self, reasoning_content: str) -> str:
        truncated = reasoning_content[-3500:]
        message = self._request_completion(
            messages=[
                {
                    "role": "user",
                    "content": (
                        "请把下面的推理草稿整理成1到3句最终中文答案。"
                        "只输出最终答案，不要解释过程，不要项目符号，不要表情。\n\n"
                        f"{truncated}"
                    ),
                }
            ],
            max_tokens=220,
        )
        return (message.get("content") or "").strip()

    @staticmethod
    def _extract_answer_from_reasoning(reasoning_content: str) -> str:
        if not reasoning_content:
            return ""

        markers = [
            "最终回答：",
            "最终回答:",
            "简洁回答：",
            "简洁回答:",
            "因此，基于证据，",
            "所以，关系是：",
            "所以，答案是：",
        ]
        for marker in markers:
            index = reasoning_content.rfind(marker)
            if index >= 0:
                candidate = reasoning_content[index + len(marker) :].strip()
                if candidate:
                    return candidate

        lines = [line.strip() for line in reasoning_content.splitlines() if line.strip()]
        if lines:
            return lines[-1]
        return ""
