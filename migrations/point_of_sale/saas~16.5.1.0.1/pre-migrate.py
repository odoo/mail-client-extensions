from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.config.settings", "is_default_pricelist_displayed")
