#!/usr/bin/env bash
# Serverda ishga tushiriladi (SSH kalit orqali, parolsiz):
#   ssh -p 2231 devuser@93.188.81.158 'bash -s' < deploy.sh
# Parol yoki boshqa maxfiy ma'lumotlarni bu faylga YOZMANG.
set -euo pipefail

APP_DIR=/home/devuser/apps/architect-edu/Tift_ojs_journal
BACKUP_DIR=/home/devuser/backups/$(date +%Y%m%d_%H%M%S)

cd "$APP_DIR"

# 1. Baza va media fayllarini zaxiralash (git ularni o'chirib yubormasligi uchun)
mkdir -p "$BACKUP_DIR"
[ -f db.sqlite3 ] && cp -a db.sqlite3 "$BACKUP_DIR/"
[ -d media ] && cp -a media "$BACKUP_DIR/"
echo "Zaxira: $BACKUP_DIR"

# 2. Kodni yangilash
git fetch origin
git reset --hard origin/main

# 3. Zaxiradan qaytarish (agar git o'chirgan bo'lsa)
[ -f "$BACKUP_DIR/db.sqlite3" ] && [ ! -f db.sqlite3 ] && cp -a "$BACKUP_DIR/db.sqlite3" .
[ -d "$BACKUP_DIR/media" ] && cp -an "$BACKUP_DIR/media" . 2>/dev/null || true

# 4. Kutubxonalar, migratsiyalar, statik fayllar
# makemigrations serverda ishlatilmaydi — migratsiyalar lokalda yaratilib commit qilinadi
./venv/bin/pip install -q -r requirements.txt
./venv/bin/python manage.py migrate --noinput
./venv/bin/python manage.py collectstatic --noinput
./venv/bin/python populate_editorial_board.py
./venv/bin/python insert_categories.py
./venv/bin/python update_pages.py

# 5. Servisni qayta ishga tushirish (sudoers da parolsiz ruxsat bo'lishi kerak)
if sudo -n systemctl restart tift-journal.service 2>/dev/null; then
    echo "Servis qayta ishga tushirildi: $(systemctl is-active tift-journal.service)"
else
    echo "DIQQAT: servisni qo'lda qayta ishga tushiring: sudo systemctl restart tift-journal.service"
fi
