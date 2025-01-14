from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.view_task_form2_inherit_sale_timesheet")
