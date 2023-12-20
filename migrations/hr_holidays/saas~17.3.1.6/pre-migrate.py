from odoo.upgrade import util


def migrate(cr, version):
    util.force_noupdate(cr, "hr_holidays.group_hr_holidays_user", noupdate=False)
