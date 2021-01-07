# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_expense_sheet", "approval_date", "timestamp without time zone")
    cr.execute(
        """
            UPDATE hr_expense_sheet
               SET approval_date = write_date
             WHERE state IN ('approve', 'post', 'done')
        """
    )
