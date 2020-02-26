# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_asset", "book_value", "float8")
    util.create_column(cr, "account_asset", "acquisition_date", "date")
    util.create_column(cr, "account_asset", "disposal_date", "date")
    util.create_column(cr, "account_move", "asset_value_change", "boolean")
    util.create_column(cr, "res_company", "gain_account_id", "int4")
    util.create_column(cr, "res_company", "loss_account_id", "int4")

    util.rename_field(cr, "account.asset", "value", "original_value")
    util.rename_field(cr, "asset.modify", "resume_date", "date")

    util.remove_field(cr, "account.asset", "display_warning_account_type")
    util.remove_field(cr, "account.move", "deferred_revenue_ids")
    util.remove_field(cr, "account.move", "number_deferred_revenue_ids")
    util.remove_field(cr, "account.move", "draft_deferred_revenue_ids")
    util.remove_field(cr, 'account.asset.pause', "action")
