from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "l10n_mx_edi.view_out_invoice_tree_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.view_out_credit_note_tree_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.view_in_invoice_bill_tree_inherit_l10n_mx_edi")
    util.remove_view(cr, "l10n_mx_edi.view_in_invoice_refund_tree_inherit_l10n_mx_edi")
