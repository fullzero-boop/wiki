#!/bin/bash
# wiki-autosync.sh — Auto-sync Obsidian Wiki ↔ LightRAG
# Runs: git pull → detect deleted files → remove from LightRAG → re-ingest changed
# Scheduled via cron on server

set -e

WIKI_DIR="/data/lightrag/wiki"
LIGHTRAG_PROJECT="/data/lightrag/project"
INGEST_PY="/data/lightrag/wiki/ingest.py"
TRACK_FILE="$WIKI_DIR/.lightrag-track.json"
LOG_FILE="$WIKI_DIR/log.md"

cd "$WIKI_DIR"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Wiki Auto-Sync ==="

# 1. Git pull (fetch latest from GitHub)
echo "--- Git pull ---"
git pull origin main 2>&1 || echo "WARN: git pull failed (will retry next cycle)"

# 2. Check for deleted files
echo "--- Check deleted files ---"
CHANGED=0
if [ -f "$TRACK_FILE" ]; then
    # Get list of files in track
    TRACKED_FILES=$(python3 -c "
import json
track = json.load(open('$TRACK_FILE'))
for k in track:
    print(k)
")
    
    for REL_PATH in $TRACKED_FILES; do
        FULL_PATH="$WIKI_DIR/$REL_PATH"
        if [ ! -f "$FULL_PATH" ]; then
            DOC_ID=$(python3 -c "
import json
track = json.load(open('$TRACK_FILE'))
print(track.get('$REL_PATH', {}).get('lightrag_doc_id', ''))
")
            if [ -n "$DOC_ID" ]; then
                echo "  DELETED: $REL_PATH (doc_id: ${DOC_ID:0:16})"
                # Remove from LightRAG
                python3 -c "
import json, os
# Remove from all kv_stores
for store in ['kv_store_full_docs', 'kv_store_doc_status', 'kv_store_text_chunks']:
    f = '$LIGHTRAG_PROJECT/$store.json'
    if os.path.exists(f):
        data = json.load(open(f))
        if '$DOC_ID' in data:
            del data['$DOC_ID']
            json.dump(data, open(f, 'w'), ensure_ascii=False)
            print(f'    Removed from {store}')
        # Also remove by full_doc_id from text_chunks
        if store == 'kv_store_text_chunks':
            to_del = [k for k, v in data.items() if v.get('full_doc_id') == '$DOC_ID']
            for k in to_del:
                del data[k]
            if to_del:
                json.dump(data, open(f, 'w'), ensure_ascii=False)
                print(f'    Removed {len(to_del)} chunks by full_doc_id')
"
                # Remove from track
                python3 -c "
import json
track = json.load(open('$TRACK_FILE'))
del track['$REL_PATH']
json.dump(track, open('$TRACK_FILE', 'w'), indent=2, ensure_ascii=False)
print('    Removed from track')
"
                CHANGED=1
            fi
        fi
    done
fi

# 3. Check for new/modified files
echo "--- Check new/modified files ---"
python3 -c "
import json, os, time, asyncio
from pathlib import Path

WIKI_DIR = Path('$WIKI_DIR')
TRACK_FILE = '$TRACK_FILE'

track = {}
if os.path.exists(TRACK_FILE):
    track = json.load(open(TRACK_FILE))

import sys
sys.path.insert(0, str(WIKI_DIR))
from ingest import insert_lightrag

new_or_changed = 0
for md_file in sorted(WIKI_DIR.rglob('*.md')):
    rel_path = str(md_file.relative_to(WIKI_DIR))
    name = md_file.name
    if name in ('index.md', 'log.md', '.lightrag-track.json'):
        continue
    
    # Check if new or changed
    old_id = track.get(rel_path, {}).get('lightrag_doc_id', '')
    old_title = track.get(rel_path, {}).get('title', '')
    content = md_file.read_text()
    
    is_new = rel_path not in track
    is_changed = False
    if not is_new:
        # Check if content hash changed (simple check)
        old_content = ''
        docs = json.load(open('$LIGHTRAG_PROJECT/kv_store_full_docs.json'))
        if old_id in docs:
            old_content = docs[old_id].get('content', '')
        if old_content != content:
            is_changed = True
            print(f'  MODIFIED: {rel_path}')
    
    if is_new:
        print(f'  NEW: {rel_path}')
    
    if is_new or is_changed:
        title = md_file.stem
        asyncio.run(insert_lightrag(content, title, rel_path))
        time.sleep(1)
        new_or_changed += 1

if new_or_changed == 0:
    print('  No new/modified files')
else:
    print(f'  Processed {new_or_changed} files')
" 2>&1

# 4. Add to log
echo "--- Log ---"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
echo "- $TIMESTAMP — Auto-sync: wiki ↔ LightRAG synced" >> "$LOG_FILE"

# 5. Commit track + log changes
echo "--- Git commit ---"
git add .lightrag-track.json log.md 2>/dev/null
if ! git diff --cached --quiet; then
    git commit -m "auto-sync: wiki ↔ LightRAG synced at $(date '+%Y-%m-%d %H:%M')" --quiet
    git push origin main 2>&1 || echo "WARN: git push failed"
    echo "  Committed and pushed"
else
    echo "  No changes to commit"
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] === Done ==="
