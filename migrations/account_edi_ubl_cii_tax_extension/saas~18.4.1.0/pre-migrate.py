from odoo.upgrade import util


def migrate(cr, version):
    # Some codes were added with underscores instead of dashes.
    FIX_WRONG_CODES_MAPPING = {
        "VATEX_EU_AE": "VATEX-EU-AE",
        "VATEX_EU_D": "VATEX-EU-D",
        "VATEX_EU_F": "VATEX-EU-F",
        "VATEX_EU_G": "VATEX-EU-G",
        "VATEX_EU_I": "VATEX-EU-I",
        "VATEX_EU_IC": "VATEX-EU-IC",
        "VATEX_EU_O": "VATEX-EU-O",
        "VATEX_EU_J": "VATEX-EU-J",
        "VATEX_FR-FRANCHISE": "VATEX-FR-FRANCHISE",
        "VATEX_FR-CNWVAT": "VATEX-FR-CNWVAT",
    }
    util.change_field_selection_values(
        cr,
        "account.tax",
        "ubl_cii_tax_exemption_reason_code",
        FIX_WRONG_CODES_MAPPING,
    )
