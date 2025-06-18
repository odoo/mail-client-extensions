from odoo.upgrade import util


def migrate(cr, version):
    # Remove UBL templates
    util.remove_view(cr, "l10n_co_edi_mandate.ubl_20_CommonLineType_mandate")
