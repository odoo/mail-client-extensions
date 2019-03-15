# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.merge_module(cr, "stock_zebra", "stock")

    if not util.has_enterprise():
        return

    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("mrp{_zebra,}.label_production_view"))
    util.rename_xmlid(cr, *eb("mrp{_zebra,}.label_manufacture_template"))
    util.rename_xmlid(cr, *eb("mrp_{zebra,workorder}.quality_point_print_labels"))
    util.rename_xmlid(cr, *eb("mrp_{zebra,workorder}.test_type_print_label"))
    util.remove_view(cr, "mrp_zebra.mrp_workorder_view_form_tablet_printers")

    util.remove_module(cr, "mrp_zebra")
