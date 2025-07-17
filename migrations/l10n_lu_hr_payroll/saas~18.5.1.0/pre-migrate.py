from odoo.upgrade import util


def migrate(cr, version):
    util.change_field_selection_values(
        cr,
        "res.company",
        "l10n_lu_accident_insurance_factor",
        {"0.9": "0.85"},
    )
