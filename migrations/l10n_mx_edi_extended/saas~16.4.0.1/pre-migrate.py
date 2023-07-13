from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(
        cr,
        "l10n_mx_edi_extended.view_account_journal_form_inherit_l10n_mx_edi_extended",
        "l10n_mx_edi_extended.account_journal_form_inherit_l10n_mx_edi_extended",
    )
    util.rename_xmlid(
        cr,
        "l10n_mx_edi_extended.view_picking_edi_form_comex",
        "l10n_mx_edi_extended.stock_picking_form_inherit_l10n_mx_edi_stock_extended",
    )
