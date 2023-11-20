from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_work_entry_holidays.hr_leave_view_tree_inherit_work_entry")
