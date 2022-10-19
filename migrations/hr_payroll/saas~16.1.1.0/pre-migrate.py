# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_payslip", "gross_wage", "double precision")

    # In case there are several lines with the same code
    # just take one of them, the sheet makes no sense,
    # so it's not a big deal to display an invalid value
    cr.execute(
        """
        UPDATE hr_payslip p
          SET gross_wage = COALESCE(l.total, 0.0)
          FROM hr_payslip_line l
         WHERE l.slip_id = p.id
          AND l.code = 'GROSS'
    """
    )
