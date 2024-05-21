from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.employee.base", "name_work_location_display")
