# -*- coding: utf-8 -*-
from lxml import etree, html
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    snip = util.import_script('website/saas~11.5.1.0/snippets.py')
    utf8_parser = html.HTMLParser(encoding="utf-8")  # will allow to use `.classes` property

    for expr, fixer in snip.FIXERS.items():

        cr.execute(
            """
            SELECT id, content
              FROM blog_post
             WHERE content LIKE %s
        """, [expr]
        )

        for blog_id, content in cr.fetchall():
            body = html.fromstring(content, parser=utf8_parser)
            fixer(body)
            body = etree.tostring(body, encoding="unicode")
            cr.execute("UPDATE blog_post SET content = %s WHERE id = %s", [body, blog_id])
