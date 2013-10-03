# -*- coding: utf-8 -*-
import urlparse
def migrate(cr, version):
    cr.execute("SELECT value FROM ir_config_parameter WHERE key=%s", ('web.base.url',))
    base_url = cr.fetchone()
    if not base_url:
        return

    scheme = urlparse.urlsplit(base_url[0] or '').scheme
    if scheme != 'https':
        return

    cr.execute("SELECT id, pad_server FROM res_company WHERE pad_server IS NOT NULL")
    for cid, url in cr.fetchall():
        up = urlparse.urlsplit(url)
        if up.scheme != scheme:
            url = urlparse.urlunsplit((scheme,) + up[1:])
            cr.execute("UPDATE res_company SET pad_server=%s WHERE id=%s", (url, cid))
