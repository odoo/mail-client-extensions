# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_field(cr, "hr.contract", "time_credit_full_time_wage")
    util.remove_field(cr, "hr.contract.history", "time_credit_full_time_wage")
