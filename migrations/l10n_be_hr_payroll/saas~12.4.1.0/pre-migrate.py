# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("l10n_be_hr_payroll.cp200_employees_termination_fees_expati{e,ate}"))

    util.create_column(cr, "hr_contract", "transport_mode_private_car", "boolean")
    util.create_column(cr, "hr_contract", "time_credit", "boolean")
    util.create_column(cr, "hr_contract", "work_time_rate", "varchar")
    cr.execute("UPDATE hr_contract SET transport_mode_private_car = false, time_credit = false")

    util.remove_field(cr, "hr.contract", "mobile_plus")
    util.remove_field(cr, "res.config.settings", "default_mobile_plus")
