# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.parallel_execute(
        cr,
        util.explode_query_range(
            cr,
            """
            UPDATE account_move m
               SET team_id = i.team_id,
                   partner_shipping_id = i.partner_shipping_id
              FROM account_invoice i
             WHERE i.move_id = m.id
            """,
            table="account_move",
            alias="m",
        ),
    )
