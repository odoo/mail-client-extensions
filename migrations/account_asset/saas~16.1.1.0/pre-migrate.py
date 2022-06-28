# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "linked_asset_type")
    util.rename_field(cr, "account.move", "draft_asset_ids", "draft_asset_exists")
    util.rename_field(cr, "account.move", "number_asset_ids", "count_asset")
