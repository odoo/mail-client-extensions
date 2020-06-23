# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "approval.category", "has_item", "has_product")
    util.create_column(cr, "approval_category", "approval_type", "varchar")
    util.create_column(cr, "approval_category", "automated_sequence", "boolean")
    util.create_column(cr, "approval_category", "sequence_code", "varchar")
    util.create_column(cr, "approval_category", "sequence_id", "integer")

    # items on requests are handled in post- script
