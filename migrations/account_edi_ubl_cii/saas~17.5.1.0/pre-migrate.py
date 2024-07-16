from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "res.partner",
        "peppol_eas",
        {"0037": "0216", "0215": "0216"},
    )
