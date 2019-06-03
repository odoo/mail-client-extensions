# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("account_asset.view_invoice_{asset_category,supplier_form_asset_inherit}"))
    util.remove_view(cr, 'account_asset.view_product_template_form_inherit')

    util.remove_record(cr, 'account_asset.account_asset_cron')
    util.remove_record(cr, 'account_asset.account_asset_cron_ir_actions_server')
