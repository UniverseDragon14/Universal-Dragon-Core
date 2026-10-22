#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail

SOURCE_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd -P)"
TARGET_DIR="${DRAGON_ROOM_MAGIC_HOME:-$HOME/dragon-room-magic-v1}"
BACKUP_ROOT="${DRAGON_ROOM_MAGIC_BACKUPS:-$HOME/.dragon-magic-backups}"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
BACKUP_DIR="$BACKUP_ROOT/$STAMP"

FILES=(
  awaken.html
  awaken-v3.sh
  voice-eleven-v3.sh
)

log() {
  printf '%s\n' "$*"
}

for file in "${FILES[@]}"; do
  if [ ! -s "$SOURCE_DIR/$file" ]; then
    log "STOP: source missing: $file"
    exit 1
  fi
done

bash -n "$SOURCE_DIR/awaken-v3.sh"
bash -n "$SOURCE_DIR/voice-eleven-v3.sh"

mkdir -p "$TARGET_DIR" "$BACKUP_ROOT"
chmod 700 "$TARGET_DIR" "$BACKUP_ROOT" 2>/dev/null || true

backup_count=0
for file in "${FILES[@]}"; do
  if [ -e "$TARGET_DIR/$file" ] || [ -L "$TARGET_DIR/$file" ]; then
    if [ "$backup_count" -eq 0 ]; then
      mkdir -p "$BACKUP_DIR"
      chmod 700 "$BACKUP_DIR" 2>/dev/null || true
    fi

    cp -p "$TARGET_DIR/$file" "$BACKUP_DIR/$file"
    backup_count=$((backup_count + 1))
  fi
done

for file in "${FILES[@]}"; do
  tmp="$TARGET_DIR/.${file}.install.$$"
  cp "$SOURCE_DIR/$file" "$tmp"

  case "$file" in
    *.sh) chmod 700 "$tmp" ;;
    *) chmod 600 "$tmp" ;;
  esac

  mv -f "$tmp" "$TARGET_DIR/$file"
done

if [ ! -s "$TARGET_DIR/dragon-awaken.wav" ] && command -v ffmpeg >/dev/null 2>&1; then
  ffmpeg -y -v error \
    -f lavfi -i "sine=frequency=72:duration=1.8" \
    -f lavfi -i "sine=frequency=144:duration=1.2" \
    -filter_complex \
    "[0:a]volume=0.55[a0];[1:a]volume=0.22,adelay=350|350[a1];[a0][a1]amix=inputs=2:duration=longest,afade=t=in:st=0:d=0.15,afade=t=out:st=1.35:d=0.4" \
    -ar 44100 \
    -ac 2 \
    "$TARGET_DIR/dragon-awaken.wav"
  chmod 600 "$TARGET_DIR/dragon-awaken.wav" 2>/dev/null || true
  log "PROCEDURAL_SOUND=CREATED"
else
  log "PROCEDURAL_SOUND=PRESERVED_OR_SKIPPED"
fi

bash -n "$TARGET_DIR/awaken-v3.sh"
bash -n "$TARGET_DIR/voice-eleven-v3.sh"
test -s "$TARGET_DIR/awaken.html"

log "TARGET=$TARGET_DIR"
log "BACKUP_FILES=$backup_count"
if [ "$backup_count" -gt 0 ]; then
  log "BACKUP_DIR=$BACKUP_DIR"
fi
log "SECRET_FILES_TOUCHED=NO"
log "ROOM_MAGIC_HANDOFF_INSTALL=PASS"
