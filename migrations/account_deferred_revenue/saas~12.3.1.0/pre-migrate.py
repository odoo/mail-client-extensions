# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    module = "account_asset" if util.version_gte("saas~12.5") else "account_deferred_revenue"
    util.remove_view(cr, module + ".view_product_template_form_inherit")
    util.remove_view(cr, module + ".view_account_invoice_asset_form")
    util.remove_view(cr, module + ".view_invoice_revenue_recognition_category")
    util.remove_view(cr, module + ".res_config_settings_view_form")
