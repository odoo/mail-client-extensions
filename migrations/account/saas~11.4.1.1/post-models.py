# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    #Partner_id was a required field until this version
    #In every migration, every invoice will have a partner_id
    cr.execute("""
        UPDATE account_invoice a
        SET vendor_display_name = p.name
        FROM res_partner p
        WHERE p.id=a.partner_id
    """)
