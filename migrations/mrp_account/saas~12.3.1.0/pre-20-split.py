# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    models = ["mrp_cost_structure", "product_template_cost_structure"]
    records = """
        action_cost_struct_mrp_production
        action_cost_struct_product_template
    """
    views = """
        mrp_cost_structure
        product_template_cost_structure
        mrp_workcenter_view_inherit
        mrp_production_form_inherit_view6
        product_product_inherit_form_view_cost_structure
    """

    if util.has_enterprise():
        for model in models:
            util.move_model(cr, "report.mrp_account.%s" % model, "mrp_account", "mrp_account_enterprise")
            util.rename_model(cr, *eb("report.mrp_account{,_enterprise}.%s" % model), rename_table=False)

        for xid in util.splitlines(records + "\n" + views):
            util.rename_xmlid(cr, *eb("mrp_account{,_enterprise}.%s" % xid))
    else:
        for record in util.splitlines(records):
            util.remove_record(cr, "mrp_account.%s" % record)
        for view in util.splitlines(views):
            util.remove_view(cr, "mrp_account.%s" % view)
        for model in models:
            util.remove_model(cr, "report.mrp_account.%s" % model)
