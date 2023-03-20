# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM res_groups_implied_rel
         WHERE gid=%s
           AND hid=%s
        """,
        [util.ref(cr, "base.group_user"), util.ref(cr, "stock.group_stock_multi_locations")],
    )
    is_group_implied = bool(cr.fetchone())
    views = [
        util.ref(cr, "stock.stock_location_view_tree2_editable"),
        util.ref(cr, "stock.stock_location_view_form_editable"),
    ]
    cr.execute("UPDATE ir_ui_view SET active=%s WHERE id IN %s", [not is_group_implied, tuple(views)])
