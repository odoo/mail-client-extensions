from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "sale_order", "l10n_mx_edi_cfdi_to_public", "boolean")
    util.create_column(cr, "sale_order", "l10n_mx_edi_usage", "varchar", default="S01")
