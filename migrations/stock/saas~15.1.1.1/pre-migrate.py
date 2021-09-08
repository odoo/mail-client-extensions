# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "stock.picking", "move_lines", "move_ids")
    util.create_column(cr, "stock_picking_type", "auto_show_reception_report", "boolean")

    cr.execute(
        "SELECT 1 FROM res_groups_implied_rel WHERE gid=%s AND hid=%s",
        [util.ref(cr, "base.group_user"), util.ref(cr, "stock.group_auto_reception_report")],
    )
    if cr.rowcount:
        cr.execute(
            "UPDATE stock_picking_type SET auto_show_reception_report = true WHERE code in ('internal', 'incoming')"
        )

    util.remove_record(cr, "stock.group_auto_reception_report")
    util.remove_field(cr, "res.config.settings", "group_stock_auto_reception_report")
