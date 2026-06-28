#!/usr/bin/env bash
# Deploy marketing-brain to GitHub. Your credentials never leave your machine.
#
# Easiest (no token in plain text):
#   gh auth login          # browser OAuth
#   ./deploy.sh
#
# Token path (use a FRESH fine-grained PAT with "Contents: read/write"):
#   export GITHUB_TOKEN=ghp_xxx
#   ./deploy.sh
set -euo pipefail
REPO="${1:-hemantsatishjadhav06-ai/marketing-brain}"
NAME="${REPO#*/}"
git init -q
git add .
git -c user.email="dev@local" -c user.name="marketing-brain" commit -q -m "marketing-brain v0.1" || true
git branch -M main
if command -v gh >/dev/null 2>&1 && gh auth status >/dev/null 2>&1; then
  gh repo create "$REPO" --public --source=. --remote=origin --push
else
  : "${GITHUB_TOKEN:?Set GITHUB_TOKEN to a fresh PAT, or run 'gh auth login' first}"
  curl -sf -H "Authorization: Bearer $GITHUB_TOKEN" -H "Accept: application/vnd.github+json" \
       https://api.github.com/user/repos -d "{\"name\":\"$NAME\",\"private\":false}" >/dev/null || true
  git remote add origin "https://github.com/$REPO.git" 2>/dev/null || true
  git push "https://x-access-token:${GITHUB_TOKEN}@github.com/${REPO}.git" main
fi
echo "Pushed. Watch CI go green: https://github.com/$REPO/actions"
