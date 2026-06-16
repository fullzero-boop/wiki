#!/usr/bin/env python3
"""wiki-sync.py: sync new/changed files from wiki to LightRAG API"""
import json, hashlib, os, sys, time, subprocess
from pathlib import Path

WIKI_DIR = Path("/data/lightrag/wiki")
TRACK_FILE = WIKI_DIR / ".lightrag-track.json"
API_URL = "http://localhost:18888"
LOG_FILE = WIKI_DIR / "sync.log"
EXCLUDE = {"index.md", "log.md", ".lightrag-track.json"}

def log(msg):
    ts = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as f:
        f.write(f"[{ts}] {msg}\n")
    print(f"[{ts}] {msg}")

def load_track():
    if TRACK_FILE.exists():
        return json.loads(TRACK_FILE.read_text())
    return {}

def save_track(track):
    TRACK_FILE.write_text(json.dumps(track, ensure_ascii=False, indent=2))

def file_hash(path):
    return hashlib.md5(Path(path).read_bytes()).hexdigest()

def sync():
    # Clean tracker: remove entries for deleted files
    existing = {str(p.relative_to(WIKI_DIR)) for p in WIKI_DIR.rglob("*.md") if ".git" not in str(p)}
    deleted = [k for k in track if k not in existing]
    for k in deleted:
        log(f"  REMOVE (deleted): {k}")
        del track[k]
    if deleted:
        save_track(track)
    track = load_track()
    synced = 0
    
    for md_file in sorted(WIKI_DIR.rglob("*.md")):
        rel_path = str(md_file.relative_to(WIKI_DIR))
        if md_file.name in EXCLUDE or ".git" in rel_path:
            continue
        
        title = md_file.stem
        cur_hash = file_hash(md_file)
        tracked = track.get(rel_path, {})
        
        if tracked.get("hash") == cur_hash:
            continue  # unchanged
        
        content = md_file.read_text()
        log(f"Syncing: {rel_path} (title={title})")
        
        # Call LightRAG API
        import urllib.request
        payload = json.dumps({"title": title, "text": content}).encode()
        req = urllib.request.Request(
            f"{API_URL}/insert",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        
        try:
            resp = urllib.request.urlopen(req, timeout=120)
            result = json.loads(resp.read())
            doc_id = result.get("doc_id", "")
            log(f"  OK: doc_id={doc_id[:20]}")
            
            track[rel_path] = {
                "hash": cur_hash,
                "title": title,
                "doc_id": doc_id,
                "synced_at": time.strftime("%Y-%m-%d %H:%M:%S")
            }
            save_track(track)
            synced += 1
        except Exception as e:
            log(f"  FAIL: {e}")
        
        time.sleep(2)
    
    log(f"Sync complete: {synced} files synced")
    return synced

if __name__ == "__main__":
    sync()
