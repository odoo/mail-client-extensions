from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "l10n_in_ewaybill", "is_sent_through_irn", "boolean")
