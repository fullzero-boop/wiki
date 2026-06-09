#!/bin/bash
cd /data/lightrag/wiki || exit 1
if ! git diff --quiet HEAD; then
    git add -A
    git commit -m "auto: wiki update 20:26" --quiet
    git push --quiet origin main 2>/dev/null
    echo "вт 09 июнь 2026 20:26:45 UTC: Committed changes"
fi
