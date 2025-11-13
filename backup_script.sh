#!/bin/bash
# M3U Matrix All-In-One - Automated Backup Script
# Creates timestamped backups and keeps last 7 days

DATE=$(date +%Y-%m-%d_%H-%M-%S)
BACKUP_DIR="backups"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

echo "📦 Creating backup: backup_$DATE.tar.gz"

# Create timestamped archive of important files
tar -czf "$BACKUP_DIR/backup_$DATE.tar.gz" \
  --exclude='node_modules' \
  --exclude='.git' \
  --exclude='logs/*' \
  --exclude='temp/*' \
  --exclude='*.log' \
  src/ \
  templates/ \
  generated_pages/ \
  *.m3u \
  *.m3u8 \
  *.md \
  requirements.txt \
  package.json \
  .gitignore \
  run_m3u_matrix.sh

echo "✅ Backup created: $BACKUP_DIR/backup_$DATE.tar.gz"

# Show backup size
du -h "$BACKUP_DIR/backup_$DATE.tar.gz"

# Keep only last 7 days of backups
echo "🧹 Cleaning old backups (keeping last 7 days)..."
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +7 -delete

# Count remaining backups
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/backup_*.tar.gz 2>/dev/null | wc -l)
echo "📊 Total backups: $BACKUP_COUNT"

echo ""
echo "✨ Backup complete!"
echo "To restore: tar -xzf $BACKUP_DIR/backup_$DATE.tar.gz"
