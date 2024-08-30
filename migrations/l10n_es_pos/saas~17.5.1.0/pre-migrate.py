from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "pos.config", "l10n_es_simplified_invoice_limit")

    util.remove_field(cr, "res.config.settings", "pos_l10n_es_simplified_invoice_limit")
    util.remove_field(cr, "res.config.settings", "pos_is_spanish")
