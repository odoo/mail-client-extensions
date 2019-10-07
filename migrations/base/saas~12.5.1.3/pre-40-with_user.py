# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute(r"""
        UPDATE ir_act_server
           SET code = regexp_replace(code, '\.sudo\((?!True\)|False\)|\))', '.with_user(\1')
         WHERE code ~ '\.sudo\((?!True\)|False\)|\))'
    """)

    if util.column_exists(cr, "mail_template", "body_html"):
        cr.execute(r"""
            UPDATE mail_template
               SET body_html = regexp_replace(body_html, '\.sudo\((?!True\)|False\)|\))', '.with_user(\1')
             WHERE body_html ~ '\.sudo\((?!True\)|False\)|\))'
        """)
