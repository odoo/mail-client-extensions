# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "transport_mode_train", "boolean")
    util.create_column(cr, "hr_contract", "train_transport_employee_amount", "numeric")
    util.create_column(cr, "hr_contract", "train_transport_reimbursed_amount", "numeric")
    util.create_column(cr, "hr_contract", "has_laptop", "boolean")
