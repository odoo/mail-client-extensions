from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_work_entry.work_entry_type_attendance")
    util.force_noupdate(cr, "hr_work_entry.overtime_work_entry_type")
