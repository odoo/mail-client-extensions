# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):

    util.create_column(cr, "hr.leave", "request_date_from", "date")
    util.create_column(cr, "hr.leave", "request_date_to", "date")
    util.create_column(cr, "hr_leave", "request_unit_all", "varchar")
    util.create_column(cr, "hr_leave", "request_unit_day", "varchar")
    cr.execute("""
        UPDATE hr_leave
           SET request_date_from=date_from,
               request_date_to=date_to,
               request_unit_all='period',
               request_unit_day='period'
    """)

    if not util.table_exists(cr, "hr_leave_allocation"):
        # from before saas~11.2, nothing to do
        return

    util.create_column(cr, "hr_leave_allocation", "accrual", "boolean")
    util.create_column(cr, "hr_leave_allocation", "number_per_interval", "int4")
    util.create_column(cr, "hr_leave_allocation", "interval_number", "int4")
    util.create_column(cr, "hr_leave_allocation", "unit_per_interval", "varchar")
    util.create_column(cr, "hr_leave_allocation", "interval_unit", "varchar")

    cr.execute("""
        UPDATE hr_leave_allocation
           SET accrual=false,
               number_per_interval=1,
               interval_number=1,
               unit_per_interval='hours',
               interval_unit='weeks'
    """)
