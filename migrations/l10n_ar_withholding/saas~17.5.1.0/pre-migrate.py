from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_ar_withholding.view_tax_form")
