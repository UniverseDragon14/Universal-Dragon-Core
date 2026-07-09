#!/usr/bin/env bash
set -e

BRAIN="$HOME/novakutty-dragon-brain"
APPROVAL="$HOME/novakutty-whatsapp-approval"

echo "🟢 NOVA Kutty WhatsApp Bot Check"
echo

echo "Brain:"
if [ -d "$BRAIN" ]; then
  echo "✅ Found: $BRAIN"
  du -sh "$BRAIN" 2>/dev/null || true
else
  echo "❌ Missing: $BRAIN"
fi

echo
echo "Approval:"
if [ -d "$APPROVAL" ]; then
  echo "✅ Found: $APPROVAL"
  du -sh "$APPROVAL" 2>/dev/null || true
else
  echo "❌ Missing: $APPROVAL"
fi

echo
echo "Recent brain files:"
find "$BRAIN" -maxdepth 2 -type f 2>/dev/null | head -20 || true

echo
echo "Recent approval files:"
find "$APPROVAL" -maxdepth 2 -type f 2>/dev/null | head -20 || true

echo
echo "✅ Check complete"
