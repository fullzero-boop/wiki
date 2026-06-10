#!/usr/bin/env python3
"""Ingest: add content to wiki + LightRAG (DeepSeek + Ollama bge-m3)."""
import os, sys, re, json, asyncio, subprocess
from pathlib import Path
from datetime import datetime

WIKI_DIR = Path("/data/lightrag/wiki")
RAW_DIR = WIKI_DIR / "raw"
LIGHTRAG_DIR = "/data/lightrag/project"
TOPICS_FILE = WIKI_DIR / "wiki-topics.json"
TRACK_FILE = WIKI_DIR / ".lightrag-track.json"

DEEPSEEK_KEY = "sk-6bb449bc23ae485d902eb57932d2dcf4"
DEEPSEEK_MODEL = "deepseek-v4-pro"

DEFAULT_TOPICS = {
    "general": ["general", "misc", "other", "разное", "общее"],
}

sys.path.insert(0, "/data/lightrag/venv/lib/python3.14/site-packages")


def load_topics():
    if TOPICS_FILE.exists():
        return json.loads(TOPICS_FILE.read_text("utf-8"))
    save_topics(DEFAULT_TOPICS)
    return DEFAULT_TOPICS


def save_topics(topics):
    TOPICS_FILE.write_text(json.dumps(topics, ensure_ascii=False, indent=2), "utf-8")


async def deepseek_chat(prompt, system_prompt=None, max_tokens=100):
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com")
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})
    resp = await client.chat.completions.create(
        model=DEEPSEEK_MODEL, messages=messages, max_tokens=max_tokens, temperature=0,
    )
    return resp.choices[0].message.content


def detect_topic(title, content):
    topics = load_topics()
    text = (title + " " + content[:1000]).lower()
    for topic_dir, keywords in topics.items():
        if any(kw.lower() in text for kw in keywords):
            return topic_dir
    topic_names = list(topics.keys()) if topics else ["none yet"]
    prompt = (
        f"Classify this content into an existing topic or suggest a NEW short topic name (English, 1-3 words).\n"
        f"Existing topics: {json.dumps(topic_names, ensure_ascii=False)}\n"
        f"Reply with ONLY the topic name.\n\n"
        f"Title: {title}\nContent preview: {content[:1500]}"
    )
    result = asyncio.run(deepseek_chat(prompt, max_tokens=30))
    topic = result.strip().strip('"').lower()
    if topic not in topics:
        kw_prompt = (
            f"Give me 5-10 short lowercase keywords for topic '{topic}'. "
            f"Reply as JSON array of strings, nothing else."
        )
        kw_result = asyncio.run(deepseek_chat(kw_prompt, max_tokens=100))
        try:
            extra_kw = json.loads(kw_result.strip())
            topics[topic] = list(set(extra_kw + [kw.lower() for kw in re.findall(r'\w{3,}', title.lower())]))
        except (json.JSONDecodeError, KeyError):
            topics[topic] = [kw.lower() for kw in re.findall(r'\w{3,}', title.lower())]
        save_topics(topics)
        print(f"  New topic auto-created: {topic}")
    return topic


def slugify(title):
    slug = re.sub(r'[^\w\s-]', '', title.lower().strip())
    slug = re.sub(r'[\s_]+', ' ', slug).strip()
    return slug.replace(" ", "-") or "untitled"


def git_commit(msg):
    subprocess.run(["git", "add", "-A"], cwd=WIKI_DIR, capture_output=True)
    subprocess.run(["git", "commit", "-m", msg], cwd=WIKI_DIR, capture_output=True)
    subprocess.run(["git", "push"], cwd=WIKI_DIR, capture_output=True)


def update_index(title, page_path):
    index_path = WIKI_DIR / "index.md"
    index_text = index_path.read_text()
    entry = f"- [[{title}]]"
    if entry not in index_text:
        lines = index_text.split("\n")
        inserted = False
        for i, line in enumerate(lines):
            if line.startswith("## ") or line.startswith("### "):
                lines.insert(i + 1, entry)
                inserted = True
                break
        if not inserted:
            lines.append(entry)
        index_path.write_text("\n".join(lines))


def update_log(action, title, details=""):
    log_path = WIKI_DIR / "log.md"
    date = datetime.now().strftime("%Y-%m-%d")
    entry = f"\n## [{date}] {action} | {title}"
    if details:
        entry += f"\n{details}"
    log_path.write_text(log_path.read_text() + entry)


def save_raw(content, title):
    date = datetime.now().strftime("%Y-%m-%d")
    filename = f"{date}-{slugify(title)}.md"
    raw_path = RAW_DIR / filename
    raw_path.write_text(content)
    return raw_path


def load_track():
    if TRACK_FILE.exists():
        return json.loads(TRACK_FILE.read_text("utf-8"))
    return {}


def save_track(track):
    TRACK_FILE.write_text(json.dumps(track, ensure_ascii=False, indent=2), "utf-8")


async def insert_lightrag(content, title, wiki_rel_path=""):
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
    await rag.ainsert(content)
    print(f"  LightRAG: inserted")

    if wiki_rel_path:
        docs_file = Path(LIGHTRAG_DIR) / "kv_store_full_docs.json"
        if docs_file.exists():
            docs = json.loads(docs_file.read_text("utf-8"))
            content_start = content[:200]
            for doc_id, doc_info in docs.items():
                if doc_info.get("content", "")[:200] == content_start:
                    track = load_track()
                    track[wiki_rel_path] = {
                        "lightrag_doc_id": doc_id, "title": title,
                        "ingested_at": datetime.now().isoformat()
                    }
                    save_track(track)
                    print(f"  Tracked: {wiki_rel_path} -> {doc_id}")
                    break


def create_wiki_page(title, content, source_url=""):
    topic = detect_topic(title, content)
    page_dir = (WIKI_DIR / topic) if topic else WIKI_DIR
    page_dir.mkdir(parents=True, exist_ok=True)
    page_path = page_dir / f"{title}.md"
    if page_path.exists():
        print(f"  WARN: {page_path.name} exists, overwriting")
        page_path.write_text(f"# {title}\n\n{content}\n")
    else:
        page_path.write_text(f"# {title}\n\n{content}\n")
    if source_url:
        with open(page_path, 'a') as f:
            f.write(f"\n\n**Source:** {source_url}")
    return page_path



def sync_all():
    """Re-ingest all wiki .md files into LightRAG (content update only)."""
    import time
    track = load_track()
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        rel_path = str(md_file.relative_to(WIKI_DIR))
        name = md_file.name
        if name in ("index.md", "log.md", ".lightrag-track.json"):
            continue
        content = md_file.read_text()
        title = md_file.stem
        print(f"  Syncing: {rel_path}")

        if rel_path in track:
            old_id = track[rel_path]["lightrag_doc_id"]
            print(f"    Updating doc_id={old_id[:16]}")

        asyncio.run(insert_lightrag(content, title, rel_path))
        print(f"    Done: {rel_path}")
        time.sleep(1)

def main():
    if len(sys.argv) >= 2 and sys.argv[1] == "--sync":
        print("Syncing all wiki files to LightRAG...")
        sync_all()
        return

    if len(sys.argv) < 2:
        print("Usage: ingest.py <title>")
        print("       ingest.py --file <path> <title>")
        print("       ingest.py --url <url> <title>")
        print("       ingest.py --sync")
        sys.exit(1)

    args = sys.argv[1:]
    if args[0] == "--file" and len(args) >= 3:
        filepath = args[1]
        title = " ".join(args[2:])
        content = Path(filepath).read_text()
    elif args[0] == "--url" and len(args) >= 3:
        url = args[1]
        title = " ".join(args[2:])
        import urllib.request
        resp = urllib.request.urlopen(url)
        content = resp.read().decode("utf-8")
    else:
        title = " ".join(args)
        print(f"Enter/paste content for '{title}'. Ctrl+D to finish:")
        lines = []
        try:
            while True:
                lines.append(input())
        except EOFError:
            pass
        content = "\n".join(lines)

    if not content.strip():
        print("No content provided.")
        sys.exit(1)

    print(f"\nIngesting: {title}")
    raw_path = save_raw(content, title)
    print(f"  Raw: {raw_path.name}")
    page_path = create_wiki_page(title, content)
    print(f"  Wiki: {page_path.name}")
    update_index(title, page_path)
    print(f"  Index updated")
    update_log("ingest", title)
    print(f"  Log updated")
    wiki_rel_path = str(page_path.relative_to(WIKI_DIR))
    asyncio.run(insert_lightrag(content, title, wiki_rel_path))
    git_commit(f"ingest: {title}")
    print(f"  Git pushed")
    print(f"\nDone! '{title}' ingested into wiki + LightRAG.")


if __name__ == "__main__":
    main()
