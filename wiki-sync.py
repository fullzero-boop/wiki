#!/usr/bin/env python3
"""
wiki-sync.py — Full wiki <-> LightRAG synchronization (DeepSeek + Ollama bge-m3).
Usage:
    python3 wiki-sync.py              # full sync (new + deleted)
    python3 wiki-sync.py --dry-run    # preview only
    python3 wiki-sync.py --all        # re-index everything
"""
import os, sys, json, subprocess, asyncio
from pathlib import Path
from datetime import datetime

WIKI_DIR = Path("/data/lightrag/wiki")
LIGHTRAG_DIR = "/data/lightrag/project"
TRACK_FILE = WIKI_DIR / ".lightrag-track.json"
DEEPSEEK_KEY = "sk-a89d8ca7c3b5490c8545a6b58993e47c"
DEEPSEEK_MODEL = "deepseek-v4-pro"

DRY_RUN = "--dry-run" in sys.argv
MODE = "all" if "--all" in sys.argv else "incremental"

sys.path.insert(0, "/data/lightrag/venv/lib/python3.14/site-packages")


def git_pull():
    result = subprocess.run(["git", "pull"], cwd=WIKI_DIR, capture_output=True, text=True)
    print(f"Git pull: {result.stdout.strip() or result.stderr.strip()}")


def load_track():
    if TRACK_FILE.exists():
        return json.loads(TRACK_FILE.read_text("utf-8"))
    return {}


def save_track(track):
    TRACK_FILE.write_text(json.dumps(track, ensure_ascii=False, indent=2), "utf-8")


def get_all_md_files():
    files = set()
    for f in WIKI_DIR.rglob("*.md"):
        if f.name not in ("index.md", "log.md", "readme.md", "README.md"):
            files.add(str(f.relative_to(WIKI_DIR)))
    return files


def get_new_files():
    all_files = get_all_md_files()
    tracked = load_track()
    return all_files - set(tracked.keys())


async def init_rag():
    from lightrag import LightRAG
    from lightrag.llm.openai import openai_complete_if_cache
    from lightrag.utils import EmbeddingFunc
    from lightrag.llm.ollama import ollama_embed

    async def llm_func(prompt, system_prompt=None, history_messages=None, **kwargs):
        return await openai_complete_if_cache(
            model=DEEPSEEK_MODEL, prompt=prompt,
            system_prompt=system_prompt, history_messages=history_messages,
            base_url="https://api.deepseek.com", api_key=DEEPSEEK_KEY, **kwargs,
        )

    rag = LightRAG(
        working_dir=LIGHTRAG_DIR, llm_model_func=llm_func, llm_model_name=DEEPSEEK_MODEL,
        embedding_func=EmbeddingFunc(
            embedding_dim=1024, max_token_size=8192,
            func=lambda texts: ollama_embed(texts, embed_model="bge-m3", host="localhost:11434"),
        ),
    )
    await rag.initialize_storages()
    return rag


async def insert_file(rag, rel_path):
    fpath = WIKI_DIR / rel_path
    if not fpath.exists():
        print(f"   File not found: {rel_path}")
        return None

    file_content = fpath.read_text("utf-8")
    title = fpath.stem

    track = load_track()
    if rel_path in track:
        print(f"   Already tracked: {rel_path}")
        return track[rel_path].get("lightrag_doc_id")

    try:
        await rag.ainsert(file_content)
        doc_id = None
        docs_file = Path(LIGHTRAG_DIR) / "kv_store_full_docs.json"
        if docs_file.exists():
            docs = json.loads(docs_file.read_text("utf-8"))
            content_start = file_content[:200]
            for did, doc_info in docs.items():
                if doc_info.get("content", "")[:200] == content_start:
                    doc_id = did
                    break

        track = load_track()
        track[rel_path] = {
            "lightrag_doc_id": doc_id or "unknown",
            "ingested_at": datetime.now().isoformat(),
            "title": title,
        }
        save_track(track)
        print(f"   Inserted: {rel_path} -> {doc_id or 'unknown'}")
        return doc_id
    except Exception as e:
        print(f"   Insert failed for {rel_path}: {e}")
        return None


def main():
    print("Wiki Sync - full synchronization")
    print(f"   Mode: {'DRY RUN' if DRY_RUN else MODE.upper()}\n")

    git_pull()
    track = load_track()

    # Detect deleted
    deleted = {}
    for rel_path, info in list(track.items()):
        full_path = WIKI_DIR / rel_path
        if not full_path.exists():
            deleted[rel_path] = info

    # Detect new files
    all_files = get_all_md_files()
    tracked = set(track.keys())
    new_files = all_files - tracked

    if not deleted and not new_files:
        print("Everything in sync. No changes detected.")
        return

    if deleted:
        print(f"{len(deleted)} deleted file(s):")
        for rel_path, info in deleted.items():
            print(f"   - {rel_path}")

    if new_files:
        print(f"{len(new_files)} new/modified file(s):")
        for f in sorted(new_files):
            print(f"   + {f}")

    if DRY_RUN:
        print("\nDry run - no changes made.")
        return

    async def run():
        rag = await init_rag()
        for rel_path in sorted(new_files):
            await insert_file(rag, rel_path)

    asyncio.run(run())

    # Remove deleted from track
    track = load_track()
    for rel_path in deleted:
        if rel_path in track:
            del track[rel_path]
    save_track(track)
    print(f"\nSync complete: {len(new_files)} inserted, {len(deleted)} removed from track.")


if __name__ == "__main__":
    main()
