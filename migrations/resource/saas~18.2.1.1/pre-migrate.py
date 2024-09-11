from odoo.upgrade import util


def migrate(cr, version):
    for field in ["is_fulltime", "work_time_rate", "hours_per_week"]:
        util.move_field_to_module(cr, "resource.calendar", field, "hr_payroll", "resource")

    util.create_column(cr, "resource_calendar", "hours_per_week", "float8")
