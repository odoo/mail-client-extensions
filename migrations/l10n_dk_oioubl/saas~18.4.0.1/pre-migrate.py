from odoo.upgrade import util


def migrate(cr, version):
    # Remove UBL templates
    util.remove_view(cr, "l10n_dk_oioubl.oioubl_PaymentMeansType")
    util.remove_view(cr, "l10n_dk_oioubl.oioubl_PaymentTermsType")
