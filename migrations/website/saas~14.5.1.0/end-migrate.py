# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # Ensure the contactus menu serves the new contactus page.
    # Note that the contactus menu URL could have been changed by the user,
    # eg to /contact
    cr.execute(
        """
        UPDATE website_menu m
           SET page_id = %s
          FROM website_page p
          JOIN ir_ui_view v ON v.id = p.view_id
         WHERE m.page_id = p.id
           AND v.key = 'website.contactus_migration_old'
    """,
        [util.ref(cr, "website.contactus_page")],
    )
