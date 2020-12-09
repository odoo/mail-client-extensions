# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_leave", "private_name", "varchar")
    util.create_column(cr, "hr_leave_allocation", "private_name", "varchar")
    cr.execute("UPDATE hr_leave SET private_name = name WHERE private_name IS NULL")
    cr.execute("UPDATE hr_leave_allocation SET private_name = name WHERE private_name IS NULL")

    util.rename_field(cr, "hr.leave.type", "validation_type", "leave_validation_type")
    util.create_column(cr, "hr_leave_type", "allocation_validation_type", "varchar")
    cr.execute(
        """
        UPDATE hr_leave_type
           SET allocation_validation_type =
            CASE
              WHEN leave_validation_type = 'no_validation' THEN 'hr'
              ELSE leave_validation_type
            END
         WHERE allocation_validation_type IS NULL
    """
    )
