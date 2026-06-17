#!/bin/bash
cd "$(dirname "$0")"
git pull origin main --ff-only 2>/dev/null
