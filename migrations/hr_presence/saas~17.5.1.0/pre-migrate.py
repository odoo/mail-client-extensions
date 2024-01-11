from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_presence.hr_employee_view_presence_search")
    util.remove_view(cr, "hr_presence.hr_employee_view_kanban")
