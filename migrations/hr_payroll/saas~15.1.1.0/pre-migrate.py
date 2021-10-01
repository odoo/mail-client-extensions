# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_payslip", "basic_wage", "double precision")
    util.create_column(cr, "hr_payslip", "net_wage", "double precision")

    # In case there are several lines with the same code
    # just taken the last one, the sheet makes no sense,
    # so it's not a big deal to display an invalid value
    cr.execute(
        """
        UPDATE hr_payslip p
          SET basic_wage = COALESCE(l.total, 0.0)
          FROM hr_payslip_line l
         WHERE l.slip_id = p.id
          AND l.code = 'BASIC'
    """
    )

    cr.execute(
        """
        UPDATE hr_payslip p
          SET net_wage = COALESCE(l.total, 0.0)
          FROM hr_payslip_line l
         WHERE l.slip_id = p.id
          AND l.code = 'NET'
    """
    )
