# -*- coding: utf-8 -*-
import odoo.upgrade.util.snippets as snip
from odoo.upgrade import util


def migrate(cr, version):
    """Reflect /website_form/ URL change inside pages and HTML fields."""
    cr.execute(
        """
        UPDATE ir_ui_view
           SET arch_db = REPLACE(arch_db, 'action="/website_form/"', 'action="/website/form/"')
         WHERE type = 'qweb'
           AND arch_db LIKE '%/website\\_form/%'
    """
    )
    for table, column in snip.get_html_fields(cr):
        cr.execute(
            f"""
            UPDATE {table}
               SET {column} = REPLACE({column}, 'action="/website_form/"', 'action="/website/form/"')
             WHERE {column} LIKE '%/website\\_form/%'
        """
        )

    # remove view moved from `website_form`
    util.remove_view(cr, "website.remove_external_snippets")
