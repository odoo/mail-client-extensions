# -*- coding: utf-8 -*-
import urlparse
def migrate(cr, version):
    cr.execute("SELECT pad_server FROM res_company WHERE pad_server LIKE %s GROUP BY pad_server", ('https://%',))
    for url, in cr.fetchall():
        up = urlparse.urlsplit(url)
        match = urlparse.urlunsplit(('http',) + up[1:]).rstrip('/') + '/%'
        cr.execute("""UPDATE note_note
                         SET note_pad_url = 'https' || substring(note_pad_url, 5)
                       WHERE note_pad_url LIKE %s
                   """, (match,))
