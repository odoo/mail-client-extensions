# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_asset.assets_search_template_extra_options")
    util.remove_view(cr, "account_asset.assets_search_template")
    util.remove_view(cr, "account_asset.main_template_assets")
    util.remove_view(cr, "account_asset.main_table_header_assets")
