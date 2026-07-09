#!/usr/bin/env bash
set -e

echo "🧠 UNIVERSAL DRAGON BRAIN CHECK"
echo "Path: $(pwd)"
echo "Branch: $(git branch --show-current 2>/dev/null || echo unknown)"
echo

echo "Identity:"
cat brain/brain_status.json 2>/dev/null || echo "brain_status.json missing"
echo

echo "QBIT NOVA C:"
if [ -d "$HOME/qbit-nova-c" ]; then
  echo "✅ Found ~/qbit-nova-c"
else
  echo "⚠️ Missing ~/qbit-nova-c"
fi

echo
echo "Stale wrapper warning:"
ls -l /usr/local/bin/nova 2>/dev/null || echo "No /usr/local/bin/nova"
ls -l "$HOME/.local/bin/qnova" 2>/dev/null || echo "No ~/.local/bin/qnova"

echo
echo "✅ Brain check complete"
