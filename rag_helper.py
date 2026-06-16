#!/usr/bin/env python3
"""
rag_helper.py — Утилита для агентов: быстрый поиск по памяти.
Приоритет: 1) wiki-файлы (мгновенно) → 2) LightRAG API (глубокий поиск).

Использование:
    from rag_helper import search
    result = search("Кто такой Bishop?")
    print(result)

Можно замокать для тестов:
    import rag_helper
    rag_helper.FAST_MODE = True  # только файлы, без API
"""
import json, os, hashlib, re, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from typing import Optional, List, Dict

WIKI_DIR = Path(os.environ.get("WIKI_DIR", "/root/wiki"))
LIGHTRAG_URL = os.environ.get("LIGHTRAG_URL", "http://172.22.0.1:18888")
LIGHTRAG_TIMEOUT = int(os.environ.get("LIGHTRAG_TIMEOUT", "60"))
FAST_MODE = os.environ.get("RAG_FAST_ONLY", "0") == "1"

# Cache для файлов
_file_cache: Dict[str, str] = {}
_file_cache_mtime: float = 0


def _refresh_file_cache():
    """Быстрая загрузка всех wiki-файлов в память."""
    global _file_cache, _file_cache_mtime
    current_mtime = max(
        (f.stat().st_mtime for f in WIKI_DIR.rglob("*.md") if ".git" not in str(f)),
        default=0,
    )
    if current_mtime <= _file_cache_mtime and _file_cache:
        return
    _file_cache = {}
    for md_file in WIKI_DIR.rglob("*.md"):
        if ".git" in str(md_file):
            continue
        rel = str(md_file.relative_to(WIKI_DIR))
        try:
            _file_cache[rel] = md_file.read_text()
        except:
            pass
    _file_cache_mtime = current_mtime


def search_files(query: str, max_results: int = 3) -> List[dict]:
    """Поиск по файлам wiki (полнотекстовый, без LLM). Мгновенно."""
    _refresh_file_cache()
    results = []
    ql = query.lower()
    for path, text in _file_cache.items():
        score = 0
        if ql in text.lower():
            score = 1 + text.lower().count(ql) * 0.01
        if score:
            # Вырезаем контекст вокруг совпадения
            idx = text.lower().find(ql)
            start = max(0, idx - 100)
            end = min(len(text), idx + len(ql) + 200)
            snippet = text[start:end]
            if start > 0:
                snippet = "..." + snippet
            if end < len(text):
                snippet = snippet + "..."
            results.append({
                "path": path,
                "score": score,
                "snippet": snippet,
                "title": Path(path).stem,
            })
    results.sort(key=lambda x: -x["score"])
    return results[:max_results]


def query_lightrag(question: str, mode: str = "hybrid") -> Optional[str]:
    """Запрос к LightRAG API."""
    params = urllib.parse.urlencode({"q": question, "mode": mode})
    url = f"{LIGHTRAG_URL}/query?{params}"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=LIGHTRAG_TIMEOUT) as resp:
            data = json.loads(resp.read())
            return data.get("response")
    except Exception as e:
        return None


def search(question: str, deep: bool = False) -> str:
    """
    Главная функция: быстрый поиск по файлам, при необходимости — LightRAG.
    
    Args:
        question: вопрос
        deep: True = форсировать LightRAG даже если файлы нашли
    
    Returns:
        строка с ответом
    """
    # 1. Быстрый поиск по файлам
    file_results = search_files(question)
    
    if file_results and not deep and not FAST_MODE:
        # Формируем ответ из файлов
        answer_parts = [f"📄 **{r['title']}**\n{r['snippet']}" for r in file_results[:2]]
        return "\n\n".join(answer_parts)
    
    if FAST_MODE and file_results:
        return "\n\n".join(
            [f"📄 **{r['title']}**\n{r['snippet']}" for r in file_results[:2]]
        )
    
    # 2. Deep search через LightRAG
    rag_result = query_lightrag(question)
    if rag_result:
        return rag_result
    
    # 3. Fallback: показываем что нашли в файлах
    if file_results:
        return "\n\n".join(
            [f"📄 **{r['title']}**\n{r['snippet']}" for r in file_results[:2]]
        )
    
    return "Ничего не найдено."


if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else "Bishop"
    print(search(q))
