# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # model `mrp.message` still there?
    views = ["view_mrp_message_kanban"] + [
        "mrp_message_view_%s" % suffix
        for suffix in {"form", "form_embedded_product", "form_embedded_bom", "tree", "search"}
    ]
    for v in views:
        util.remove_view(cr, "mrp." + v)

    util.remove_record(cr, "mrp.mrp_message_action_main")
    util.remove_menus(cr, [util.ref(cr, "mrp.message_menu")])
    util.remove_model(cr, "mrp.message")
    util.remove_field(cr, "mrp.workorder", "production_messages")
