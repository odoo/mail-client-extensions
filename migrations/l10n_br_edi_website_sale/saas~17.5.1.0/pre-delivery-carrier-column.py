from odoo.upgrade import util


def migrate(cr, version):
    # Prevent this new field from being computed, it will be empty anyways.
    util.create_column(cr, "delivery_carrier", "l10n_br_edi_transporter_id", "int4")
