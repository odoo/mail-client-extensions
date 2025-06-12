from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.job", "activities_overdue")
    util.remove_field(cr, "hr.job", "activities_today")
    util.remove_field(cr, "hr.job", "compensation")

    if util.module_installed(cr, "hr_recruitment_integration_base"):
        util.move_field_to_module(cr, "hr.job", "currency_id", "hr_recruitment", "hr_recruitment_integration_base")
    else:
        util.remove_field(cr, "hr.job", "currency_id")
