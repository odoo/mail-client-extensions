# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_payslip", "queued_for_pdf", "bool", default=False)
