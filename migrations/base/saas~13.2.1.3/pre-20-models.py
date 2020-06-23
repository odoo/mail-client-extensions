# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "ir_model", "order", "varchar")
    cr.execute("""UPDATE ir_model SET "order" = 'id'""")

    util.create_column(cr, "ir_model_fields", "group_expand", "boolean")

    util.remove_field(cr, "res.company", "account_no")
