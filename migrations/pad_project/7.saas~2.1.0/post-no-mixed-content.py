# -*- coding: utf-8 -*-
import urlparse
def migrate(cr, version):
    cr.execute("SELECT pad_server FROM res_company WHERE pad_server LIKE %s GROUP BY pad_server", ('https://%',))
    for url, in cr.fetchall():
        up = urlparse.urlsplit(url)
        match = urlparse.urlunsplit(('http',) + up[1:]).rstrip('/') + '/%'
        cr.execute("""UPDATE project_task
                         SET description_pad = 'https' || substring(description_pad, 5)
                       WHERE description_pad LIKE %s
                   """, (match,))
