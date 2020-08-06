# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "generate.simulation.link", "car_id")
    util.remove_field(cr, "generate.simulation.link", "new_car")
    util.remove_field(cr, "generate.simulation.link", "customer_relation")

    util.delete_unused(cr, "l10n_be_hr_contract_salary.l10n_be_representation_fees_value_1")
    util.remove_view(cr, "l10n_be_hr_contract_salary.assets_frontend")
    util.remove_view(cr, "l10n_be_hr_contract_salary.salary_package")
