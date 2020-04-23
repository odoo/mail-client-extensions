# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        "UPDATE hr_payroll_structure_type SET time_credit_type_id=%s WHERE time_credit_type_id IS NULL",
        [util.ref(cr, "l10n_be_hr_payroll.work_entry_type_credit_time")],
    )
