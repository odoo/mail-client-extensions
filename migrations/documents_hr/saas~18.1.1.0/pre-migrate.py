from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "hr.departure.wizard", "private_email")
