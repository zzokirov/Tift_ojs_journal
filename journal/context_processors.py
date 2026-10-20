from journal.models import Journal


def admin_journal_context(request):
    """
    Admin panelda tanlangan jurnalni aniqlaydi va sidebar menyularida
    shu jurnalga tegishli filtrlarni ta'minlaydi.
    """
    if not request.path.startswith('/admin/'):
        return {}

    # 1. Agar foydalanuvchi barcha jurnallar ro'yxatiga o'tsa:
    if request.path == '/admin/journal/journal/':
        request.session.pop('admin_active_journal_id', None)

    # 2. URL dagi standart filtrlar orqali jurnalni aniqlash
    jid = request.GET.get('journal__id__exact')
    if jid:
        try:
            request.session['admin_active_journal_id'] = int(jid)
        except (ValueError, TypeError):
            pass

    # 3. Agar jurnal sozlamalari sahifasida bo'lsa: /admin/journal/journal/<id>/change/
    path_parts = [p for p in request.path.strip('/').split('/') if p]
    if len(path_parts) >= 4 and path_parts[0] == 'admin' and path_parts[1] == 'journal' and path_parts[2] == 'journal':
        if path_parts[3].isdigit():
            try:
                request.session['admin_active_journal_id'] = int(path_parts[3])
            except (ValueError, TypeError):
                pass

    active_journal_id = request.session.get('admin_active_journal_id')
    active_journal = None
    if active_journal_id:
        try:
            active_journal = Journal.objects.filter(pk=active_journal_id).first()
        except Exception:
            pass

    all_admin_journals = Journal.objects.filter(is_active=True).order_by('display_order', 'id')

    return {
        'admin_active_journal': active_journal,
        'admin_all_journals': all_admin_journals,
    }
