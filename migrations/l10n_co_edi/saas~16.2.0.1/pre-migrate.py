from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "uom.uom", "l10n_co_edi_country_code")
