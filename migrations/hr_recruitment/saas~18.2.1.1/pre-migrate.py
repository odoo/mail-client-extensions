from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "hr_recruitment.hr_candidate_view_calendar")
