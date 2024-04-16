from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "res.partner",
        "peppol_eas",
        {"0212": "0216", "0213": "0216", "9955": "0007", "9901": "0184"},
    )
