# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_view(cr, "stock.view_pack_operation_lot_form")
    util.remove_view(cr, "stock.view_procurement_form_stock_inherit")
    util.remove_view(cr, "stock.view_procurement_tree_stock_inherit")

    # https://github.com/odoo/odoo/commit/0e4f3bb95991261c04c08e72b28430acfabdecd1
    # The content of the inherit views is merged in the base views
    mapping = {
        "procurement_group_form_view_herited": "procurement_group_form_view",
        "view_procurement_rule_tree_stock_inherit": "view_procurement_rule_tree",
        "view_procurement_rule_form_stock_inherit": "view_procurement_rule_form",
    }

    mapping_ref = {}
    for old_view, new_view in mapping.items():
        if new_view:
            old = util.ref(cr, "stock.%s" % old_view)
            new = util.ref(cr, "stock.%s" % new_view)
            if old and new:
                mapping_ref[old] = new
    util.replace_record_references_batch(cr, mapping_ref, "ir.ui.view", replace_xmlid=False)

    for view in mapping.keys():
        util.remove_view(cr, "stock.%s" % view)
