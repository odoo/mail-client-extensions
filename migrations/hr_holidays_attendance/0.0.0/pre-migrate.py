from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_between("17.0", "saas~18.1"):
        util.remove_view(cr, "hr_holidays_attendance.hr_leave_view_form_overtime")
