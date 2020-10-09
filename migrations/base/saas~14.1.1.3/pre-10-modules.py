# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.new_module(cr, "sale_sms", deps={"sale", "sms"}, auto_install=True)

    if util.has_enterprise():
        util.module_deps_diff(cr, "l10n_be_hr_payroll", plus={"hr_payroll_holidays"})
