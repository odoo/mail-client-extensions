# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
                UPDATE account_invoice a
                SET vendor_display_name = p.name
                FROM res_partner p
                WHERE p.id=a.partner_id
            """,
            table="account_invoice",
            prefix="a.",
        ),
    )
