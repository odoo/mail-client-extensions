# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.asset", "user_type_id")
    util.remove_model(cr, "account.assets.report")
    util.remove_view(cr, "account_asset.line_caret_options")
    util.remove_view(cr, "account_asset.main_template_asset_report")
