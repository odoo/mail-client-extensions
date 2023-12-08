from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "planning.slot", "work_address_id")
