# M3U Matrix All-In-One - Windows PowerShell Backup Script
# Creates daily backups and keeps last 10

$date = Get-Date -Format "yyyy-MM-dd_HH-mm-ss"
$source = "C:\Users\banamine\Videos\M3U MATRIX ALL IN ONE"
$backupRoot = "C:\Users\banamine\Videos\M3U_BACKUPS"
$backupDest = "$backupRoot\backup_$date"

Write-Host "📦 Creating backup: backup_$date" -ForegroundColor Cyan

# Create backup directory
New-Item -ItemType Directory -Force -Path $backupDest | Out-Null

# Copy files (excluding node_modules, logs, .git, temp)
Write-Host "📁 Copying files..." -ForegroundColor Yellow
robocopy $source $backupDest /E /NP /NDL /NFL `
  /XD "node_modules" ".git" ".cache" "logs" "temp" ".pythonlibs" `
  /XF "*.log" "*.pyc"

# Create ZIP archive
Write-Host "🗜️  Compressing..." -ForegroundColor Yellow
Compress-Archive -Path $backupDest -DestinationPath "$backupRoot\backup_$date.zip" -Force

# Remove uncompressed backup folder
Remove-Item -Recurse -Force $backupDest

# Show backup size
$backupSize = (Get-Item "$backupRoot\backup_$date.zip").Length / 1MB
Write-Host "✅ Backup created: $([math]::Round($backupSize, 2)) MB" -ForegroundColor Green

# Keep only last 10 backups
Write-Host "🧹 Cleaning old backups (keeping last 10)..." -ForegroundColor Yellow
Get-ChildItem "$backupRoot\backup_*.zip" | 
  Sort-Object CreationTime -Descending | 
  Select-Object -Skip 10 | 
  Remove-Item -Force

# Count remaining backups
$backupCount = (Get-ChildItem "$backupRoot\backup_*.zip").Count
Write-Host "📊 Total backups: $backupCount" -ForegroundColor Cyan

Write-Host ""
Write-Host "✨ Backup complete!" -ForegroundColor Green
Write-Host "Location: $backupRoot\backup_$date.zip" -ForegroundColor White

# Optional: Copy to external drive or OneDrive
# Uncomment and modify path as needed:
# $externalDrive = "D:\Backups\M3U_Matrix"
# Copy-Item "$backupRoot\backup_$date.zip" $externalDrive -Force
# Write-Host "💾 Also backed up to: $externalDrive" -ForegroundColor Green
