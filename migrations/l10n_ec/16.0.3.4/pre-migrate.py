from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "l10n_ec.account_l10n_ec_sri_payment",
        "l10n_ec.view_payment_method_tree",
    )
