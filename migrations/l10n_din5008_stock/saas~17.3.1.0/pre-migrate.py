from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "stock.picking", "l10n_din5008_addresses")
