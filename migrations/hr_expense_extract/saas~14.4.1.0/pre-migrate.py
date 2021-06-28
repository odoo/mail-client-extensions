# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # ===============================================================
    # Allows multiple acquirers on a bank journal (PR: 67331(odoo), 17258(enterprise))
    # ===============================================================
    util.remove_field(cr, "expense.sample.register", "payment_method_ids")

    # ===============================================================
    # Payment method improvements (PR: 72105(odoo), 18981(enterprise))
    # ===============================================================
    util.rename_field(cr, "expense.sample.register", "hide_payment", "hide_payment_method_line")

    util.remove_field(cr, "expense.sample.register", "available_payment_method_ids")

    util.remove_field(cr, "expense.sample.register", "payment_method_id")
    util.create_column(cr, "expense_sample_register", "payment_method_line_id", "int4")
