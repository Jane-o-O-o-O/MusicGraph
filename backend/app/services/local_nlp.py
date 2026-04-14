from functools import lru_cache


class LocalNlpService:
    def __init__(self) -> None:
        self._nlp = None
        self._available = False

        try:
            import spacy

            self._nlp = spacy.load("zh_core_web_md")
            self._available = True
        except Exception:
            self._nlp = None
            self._available = False

    @property
    def available(self) -> bool:
        return self._available

    def extract_candidate_terms(self, text: str) -> list[str]:
        normalized = text.strip()
        if not normalized:
            return []

        if not self._available or self._nlp is None:
            return [normalized]

        doc = self._nlp(normalized)
        candidates: list[str] = []

        for ent in doc.ents:
            value = ent.text.strip()
            if len(value) >= 2:
                candidates.append(value)

        current_tokens: list[str] = []
        for token in doc:
            if token.is_space or token.is_punct:
                if current_tokens:
                    phrase = "".join(current_tokens).strip()
                    if len(phrase) >= 2:
                        candidates.append(phrase)
                    current_tokens = []
                continue

            if token.is_stop:
                if current_tokens:
                    phrase = "".join(current_tokens).strip()
                    if len(phrase) >= 2:
                        candidates.append(phrase)
                    current_tokens = []
                continue

            text_value = token.text.strip()
            if len(text_value) >= 2:
                candidates.append(text_value)

            if token.pos_ in {"PROPN", "NOUN", "VERB", "ADJ"} and len(text_value) <= 12:
                current_tokens.append(text_value)
            elif current_tokens:
                phrase = "".join(current_tokens).strip()
                if len(phrase) >= 2:
                    candidates.append(phrase)
                current_tokens = []

        if current_tokens:
            phrase = "".join(current_tokens).strip()
            if len(phrase) >= 2:
                candidates.append(phrase)

        candidates.append(normalized)

        deduped: list[str] = []
        seen: set[str] = set()
        for candidate in sorted(candidates, key=len, reverse=True):
            key = candidate.casefold()
            if key in seen:
                continue
            seen.add(key)
            deduped.append(candidate)
        return deduped


@lru_cache
def get_local_nlp_service() -> LocalNlpService:
    return LocalNlpService()
