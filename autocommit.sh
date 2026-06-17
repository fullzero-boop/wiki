#!/bin/bash
# wiki-autocommit.sh — авто-коммит и пуш изменений wiki в GitHub
set -e

cd /data/lightrag/wiki || exit 1

# Настройки
GIT_USER="fullzero-boop"
GIT_EMAIL="fullzero-boop@users.noreply.github.com"
REPO="git@github.com:fullzero-boop/wiki.git"
BRANCH="main"

# Настройка git если первый раз
if ! git rev-parse --is-inside-work-tree 2>/dev/null; then
    git init
    git remote add origin "$REPO"
    git checkout -b "$BRANCH"
fi

git config user.name "$GIT_USER"
git config user.email "$GIT_EMAIL"

# Коммит только если есть изменения
if ! git diff --quiet HEAD 2>/dev/null || ! git diff --cached --quiet 2>/dev/null; then
    git add -A
    TIMESTAMP=$(date '+%Y-%m-%d %H:%M')
    git commit -m "Auto-commit: $TIMESTAMP"
    git push --quiet origin "$BRANCH" 2>/dev/null || echo "Push failed (will retry next time)"
    echo "$TIMESTAMP: Committed and pushed"
else
    echo "$(date '+%Y-%m-%d %H:%M'): No changes"
fi
