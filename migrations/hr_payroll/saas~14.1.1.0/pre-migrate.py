# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "hr_payslip", "has_negative_net_to_report", "boolean")

    # Related fields that become stored
    util.create_column(cr, "hr_payslip_worked_days", "name", "varchar")
    cr.execute(
        """UPDATE hr_payslip_worked_days hpwd
           SET name=hwet.name
           FROM hr_work_entry_type hwet
           WHERE hpwd.work_entry_type_id = hwet.id"""
    )

    util.create_column(cr, "hr_payslip_input", "name", "varchar")
    cr.execute(
        """UPDATE hr_payslip_input hpi
           SET name=hpit.name
           FROM hr_payslip_input_type hpit
           WHERE hpi.input_type_id = hpit.id"""
    )
