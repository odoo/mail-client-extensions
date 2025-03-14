from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "loyalty.loyalty_program_action")
