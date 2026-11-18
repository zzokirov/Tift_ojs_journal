#!/usr/bin/env bash
# Serverda cron orqali har daqiqada ishga tushadi:
#   * * * * * bash /home/devuser/apps/architect-edu/Tift_ojs_journal/auto_deploy.sh
# GitHub'dagi main yangilangan bo'lsa, deploy.sh ni ishga tushiradi.
set -euo pipefail

APP_DIR=/home/devuser/apps/architect-edu/Tift_ojs_journal
LOG=/home/devuser/deploy.log

# Bir vaqtda faqat bitta deploy
exec 9>/tmp/tift-journal-deploy.lock
flock -n 9 || exit 0

cd "$APP_DIR"
git fetch -q origin main
[ "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)" ] && exit 0

# deploy.sh o'zini git reset bilan yangilaydi, shuning uchun nusxasidan ishga tushiramiz
TMP_SCRIPT=$(mktemp)
git show origin/main:deploy.sh > "$TMP_SCRIPT"
{
    echo "===== $(date '+%F %T') deploy: $(git rev-parse --short origin/main) ====="
    bash "$TMP_SCRIPT" && echo "OK" || echo "XATO (kod $?)"
} >> "$LOG" 2>&1
rm -f "$TMP_SCRIPT"
