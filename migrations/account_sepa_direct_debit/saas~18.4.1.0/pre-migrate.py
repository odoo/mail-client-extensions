from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "account.move", "sdd_mandate_id")
