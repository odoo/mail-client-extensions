from odoo.upgrade import util


def migrate(cr, version):
    util.remove_column(cr, "hr_employee", "address_home_id")
