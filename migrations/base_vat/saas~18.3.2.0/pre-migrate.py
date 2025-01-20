from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "vies_vat_to_check")
