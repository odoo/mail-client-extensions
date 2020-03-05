# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    assert util.module_installed(cr, "industry_fsm_sale_report")  # should always be true due to dependencies
    eb = util.expand_braces

    util.move_field_to_module(
        cr, "product.template", "worksheet_template_id", "industry_fsm_report", "industry_fsm_sale_report"
    )

    util.rename_xmlid(cr, *eb("industry_fsm_{,sale_}report.view_product_timesheet_form_inherit"))

    # demo data, just in case
    util.rename_xmlid(cr, *eb("industry_fsm_{,sale_}report.fsm_template_field4"))
