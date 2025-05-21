from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "is_coa_installed")
