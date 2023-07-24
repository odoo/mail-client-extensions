from odoo.upgrade import util


def migrate(cr, version):
    if util.module_installed(cr, "hr_recruitment"):
        util.move_field_to_module(cr, "hr.employee", "newly_hired_employee", "hr_recruitment", "hr")
        util.rename_field(cr, "hr.employee", "newly_hired_employee", "newly_hired")
