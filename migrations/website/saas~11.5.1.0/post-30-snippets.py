# -*- coding: utf-8 -*-
from lxml import etree, html
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    snip = util.import_script('website/saas~11.5.1.0/snippets.py')
    utf8_parser = html.HTMLParser(encoding="utf-8")  # will allow to use `.classes` property

    for expr, fixer in snip.FIXERS.items():

        cr.execute(
            """
            SELECT i.id, i.arch_db
              FROM ir_ui_view i
              JOIN website_page w ON i.id = w.view_id
             WHERE i.arch_db LIKE %s
        """, [expr]
        )

        for view_id, arch in cr.fetchall():
            body = html.fromstring(arch, parser=utf8_parser)
            fixer(body)
            body = etree.tostring(body, encoding="unicode")
            cr.execute("UPDATE ir_ui_view  SET arch_db = %s WHERE id = %s", [body, view_id])
