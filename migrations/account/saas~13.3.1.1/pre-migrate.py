# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_field(cr, "account.move", "type", "move_type")
    util.rename_field(cr, "account.invoice.report", "type", "move_type")
    util.rename_field(cr, "account.move.line", "tag_ids", "tax_tag_ids")
