from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "sale.order", "l10n_din5008_template_data")
    util.remove_field(cr, "sale.order", "l10n_din5008_document_title")
    util.remove_field(cr, "sale.order", "l10n_din5008_addresses")
