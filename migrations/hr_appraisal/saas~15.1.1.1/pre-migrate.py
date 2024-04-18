from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "hr_employee", "next_appraisal_date")
