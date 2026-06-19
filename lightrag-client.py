import urllib.parse
#!/usr/bin/env python3
"""LightRAG Client — для агентов: быстрые запросы к RAG через API."""
import json
import urllib.request
import urllib.error
import os
from typing import Optional

# Default — host gateway для Docker контейнеров на agent-net
DEFAULT_URL = os.environ.get("LIGHTRAG_URL", "http://172.22.0.1:18888")
TIMEOUT = int(os.environ.get("LIGHTRAG_TIMEOUT", "15"))


def query(
    question: str,
    mode: str = "hybrid",
    api_url: str = DEFAULT_URL,
    timeout: int = TIMEOUT,
) -> Optional[str]:
    """
    Быстрый запрос к LightRAG.
    mode: local (только граф, быстрее) | global | hybrid (лучше)
    """
    params = urllib.parse.urlencode({"q": question, "mode": mode})
    url = f"{api_url}/query?{params}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
            return data.get("response")
    except Exception as e:
        return f"[LightRAG error] {e}"


def insert_doc(title: str, text: str, api_url: str = DEFAULT_URL) -> Optional[str]:
    """Вставить документ в LightRAG."""
    payload = json.dumps({"title": title, "text": text}).encode()
    req = urllib.request.Request(
        f"{api_url}/insert",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            data = json.loads(resp.read())
            return data.get("doc_id")
    except Exception as e:
        return f"[LightRAG insert error] {e}"


def health(api_url: str = DEFAULT_URL) -> dict:
    """Проверка доступности LightRAG."""
    try:
        req = urllib.request.Request(f"{api_url}/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return json.loads(resp.read())
    except Exception as e:
        return {"status": "error", "error": str(e)}


# CLI mode
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: lightrag-client.py <question> [mode=hybrid|local|global]")
        sys.exit(1)
    q = sys.argv[1]
    m = sys.argv[2] if len(sys.argv) > 2 else "hybrid"
    result = query(q, mode=m)
    if result:
        print(result)
    else:
        print("No response")
