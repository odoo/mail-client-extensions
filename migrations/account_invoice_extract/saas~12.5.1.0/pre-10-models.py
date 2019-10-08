# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "duplicated_vendor_ref", "varchar")
    util.rename_field(cr, "account.move", "extract_remoteid", "extract_remote_id")
