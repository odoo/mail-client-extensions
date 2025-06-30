from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.job", "activities_overdue")
    util.remove_field(cr, "hr.job", "activities_today")
