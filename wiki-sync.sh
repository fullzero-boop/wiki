#!/bin/bash
# wiki-sync.sh: sync new/changed wiki files to LightRAG via API
# Runs via cron, uses curl to FastAPI on 18888

WIKI_DIR="/data/lightrag/wiki"
TRACK_FILE="$WIKI_DIR/.lightrag-track.json"
API_URL="http://localhost:18888"
LOG_FILE="$WIKI_DIR/sync.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"
}

# Load track file
if [ -f "$TRACK_FILE" ]; then
    TRACK=$(cat "$TRACK_FILE")
else
    TRACK="{}"
fi

cd "$WIKI_DIR"

# Track file hash for the tracker itself
TRACK_HASH=$(md5sum "$TRACK_FILE" 2>/dev/null | cut -d' ' -f1)

# Find all .md files (exclude index.md, log.md, .lightrag-track.json)
# Better: handle all files - insert-wiki API needs title
find . -name '*.md' -not -path './.git/*' \
    -not -name 'index.md' -not -name 'log.md' \
    | sed 's|^\./||' | sort | while read -r relpath; do
    
    filepath="$WIKI_DIR/$relpath"
    title=$(basename "$relpath" .md)
    
    # Check if already tracked with same hash
    current_hash=$(md5sum "$filepath" | cut -d' ' -f1)
    tracked_hash=$(echo "$TRACK" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('$relpath',{}).get('hash',''))" 2>/dev/null)
    
    if [ "$current_hash" = "$tracked_hash" ]; then
        continue  # unchanged, skip
    fi
    
    log "Syncing: $relpath (title=$title)"
    
    # Read file content
    content=$(cat "$filepath")
    
    # Call LightRAG API /insert
    RESPONSE=$(curl -s -X POST "$API_URL/insert" \
        -H "Content-Type: application/json" \
        -d "$(python3 -c "import json; print(json.dumps({'title':'$title','text':'''$content'''}))")" 2>/dev/null)
    
    DOC_ID=$(echo "$RESPONSE" | python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('doc_id',''))" 2>/dev/null)
    
    if [ -n "$DOC_ID" ]; then
        log "  OK: doc_id=$DOC_ID"
        # Update tracker
        TRACK=$(echo "$TRACK" | python3 -c "
import json, sys
d = json.load(sys.stdin)
d['$relpath'] = {'hash': '$current_hash', 'title': '$title', 'doc_id': '$DOC_ID'}
print(json.dumps(d))
")
        echo "$TRACK" > "$TRACK_FILE"
    else
        log "  FAIL: $RESPONSE"
    fi
    
    sleep 2
done

log "Sync complete"
