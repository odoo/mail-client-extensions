from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.users", "allocation_count")
    util.remove_field(cr, "res.users", "current_leave_state")
