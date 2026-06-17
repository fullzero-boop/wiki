#!/bin/bash
# wiki-pull.sh — Force sync wiki from GitHub (handles divergent branches)
cd "$(dirname "$0")"
git fetch origin main 2>/dev/null
git reset --hard origin/main 2>/dev/null
