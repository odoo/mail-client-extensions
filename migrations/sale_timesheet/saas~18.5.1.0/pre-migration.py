from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "sale_timesheet.project_update_default_description")
