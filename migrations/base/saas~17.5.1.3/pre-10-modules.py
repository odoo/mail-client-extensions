from odoo.upgrade import util


def migrate(cr, version):
    util.merge_module(cr, "l10n_mx_edi_stock_extended_31", "l10n_mx_edi_stock_extended")
    util.force_upgrade_of_fresh_module(cr, "html_editor", init=False)
