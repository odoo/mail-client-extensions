from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "hr_version", "time_credit")
    util.remove_column(cr, "hr_version", "time_credit_type_id")
