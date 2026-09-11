import json
import hashlib
from pathlib import Path
from typing import Any, Optional


class SimpleJsonCache:
    """本地轻量级文件缓存，用于检索结果和 LLM 分析结果持久化。"""

    def __init__(self, cache_file: str = "storage/cache.json"):
        self.cache_path = Path(cache_file)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self._data = {}
        self._load()

    def _load(self):
        if self.cache_path.exists():
            try:
                self._data = json.loads(self.cache_path.read_text(encoding="utf-8"))
            except Exception:
                self._data = {}

    def _save(self):
        try:
            self.cache_path.write_text(
                json.dumps(self._data, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
        except Exception as exc:
            print(f"⚠ 缓存写入失败: {exc}")

    @staticmethod
    def _make_key(namespace: str, raw_key: str) -> str:
        h = hashlib.md5(raw_key.strip().lower().encode("utf-8")).hexdigest()
        return f"{namespace}:{h}"

    def get(self, namespace: str, raw_key: str) -> Optional[Any]:
        k = self._make_key(namespace, raw_key)
        return self._data.get(k)

    def set(self, namespace: str, raw_key: str, value: Any):
        k = self._make_key(namespace, raw_key)
        self._data[k] = value
        self._save()