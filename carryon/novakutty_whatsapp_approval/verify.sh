#!/bin/bash
# Novakutty WhatsApp Approval — Verification Script v5.3.3

set -e

echo "════════════════════════════════════════════════════════════"
echo "  NOVAKUTTY WHATSAPP APPROVAL — Verification v5.3.3"
echo "════════════════════════════════════════════════════════════"
echo ""

# A) Check file presence
echo "=== A) File Structure ==="
files=(
  "bot.js"
  "lib/strong_brain_bridge_v526.js"
  "lib/public_context_router_v526.js"
  "package.json"
  "README.md"
)
for f in "${files[@]}"; do
  if [ -f "$f" ]; then
    echo "  ✓ $f"
  else
    echo "  ✗ $f MISSING"
    exit 1
  fi
done
echo ""

# B) Check patch markers in bot.js
echo "=== B) Code Patches ==="
patches=(
  "NOVAKUTTY_STRONG_LINK_V5_2_6:Deep search routing"
  "NOVAKUTTY_PUBLIC_MEMORY_FOLLOWUP_V5_2_5:Follow-up detection"
  "TDZ_FIX_V526:getText before owner check"
  "HELP_MENU_V533:Owner commands"
)
for patch in "${patches[@]}"; do
  label="${patch%%:*}"
  desc="${patch##*:}"
  if grep -q "$label" bot.js; then
    echo "  ✓ $label — $desc"
  else
    echo "  ✗ $label MISSING"
    exit 1
  fi
done
echo ""

# C) Check library exports
echo "=== C) Library Exports ==="
echo "  strong_brain_bridge_v526.js:"
grep -q "askStrongBrain" lib/strong_brain_bridge_v526.js && echo "    ✓ askStrongBrain()" || exit 1
grep -q "redact" lib/strong_brain_bridge_v526.js && echo "    ✓ redact()" || exit 1

echo "  public_context_router_v526.js:"
grep -q "maybeFollowupReply" lib/public_context_router_v526.js && echo "    ✓ maybeFollowupReply()" || exit 1
grep -q "saveContext" lib/public_context_router_v526.js && echo "    ✓ saveContext()" || exit 1
grep -q "isFollowup" lib/public_context_router_v526.js && echo "    ✓ isFollowup()" || exit 1
echo ""

# D) Syntax check
echo "=== D) Node Syntax ==="
if node -c bot.js 2>&1 | grep -q "SyntaxError"; then
  echo "  ✗ bot.js has syntax errors"
  node -c bot.js
  exit 1
else
  echo "  ✓ bot.js syntax valid"
fi

if node -c lib/strong_brain_bridge_v526.js 2>&1 | grep -q "SyntaxError"; then
  echo "  ✗ strong_brain_bridge_v526.js has syntax errors"
  exit 1
else
  echo "  ✓ strong_brain_bridge_v526.js syntax valid"
fi

if node -c lib/public_context_router_v526.js 2>&1 | grep -q "SyntaxError"; then
  echo "  ✗ public_context_router_v526.js has syntax errors"
  exit 1
else
  echo "  ✓ public_context_router_v526.js syntax valid"
fi
echo ""

# E) Check memory directory structure
echo "=== E) Memory Directories ==="
mkdir -p memory/followup memory/chats audit_backup
echo "  ✓ memory/followup/ created"
echo "  ✓ memory/chats/ created"
echo "  ✓ audit_backup/ created"
echo ""

# F) Security checks (no exposed secrets)
echo "=== F) Security Audit ==="
if grep -r "sk-ant-\|gsk_\|AIza\|ya29\." bot.js lib/ 2>/dev/null | grep -v "REDACTED"; then
  echo "  ⚠ WARNING: Possible exposed keys in code (review carefully)"
else
  echo "  ✓ No hardcoded API keys detected"
fi

if grep -q "OWNER_NUMBER.*=" bot.js; then
  echo "  ✓ OWNER_NUMBER set (check env before run)"
else
  echo "  ⚠ OWNER_NUMBER not found in bot.js"
fi
echo ""

# G) Dependencies check (if npm installed)
echo "=== G) Dependencies ==="
if [ -f "package.json" ] && [ -d "node_modules" ]; then
  echo "  ✓ node_modules exists"
  if npm list whatsapp-web.js >/dev/null 2>&1; then
    echo "  ✓ whatsapp-web.js installed"
  else
    echo "  ⚠ whatsapp-web.js NOT installed — run: npm install"
  fi
else
  echo "  ⚠ Dependencies not installed — run: npm install"
fi
echo ""

# H) Summary
echo "════════════════════════════════════════════════════════════"
echo "  ✓ All checks passed!"
echo ""
echo "  Next steps:"
echo "  1. npm install"
echo "  2. export OWNER_NUMBER='+1234567890'"
echo "  3. npm run pm2-start"
echo "  4. Scan QR code"
echo "════════════════════════════════════════════════════════════"
echo ""
