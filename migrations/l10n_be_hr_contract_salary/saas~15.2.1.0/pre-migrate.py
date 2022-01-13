# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_view(cr, "l10n_be_hr_contract_salary.salary_package_canteen")
