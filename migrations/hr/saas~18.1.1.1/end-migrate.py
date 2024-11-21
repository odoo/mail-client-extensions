from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "hr_departure_reason", "reason_code")
