from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "res.partner", "l10n_mx_edi_addenda_doc")
    util.remove_field(cr, "res.partner", "l10n_mx_edi_addenda", drop_column=False)
    util.remove_field(cr, "ir.ui.view", "l10n_mx_edi_addenda_flag", drop_column=False)
    util.remove_view(cr, "l10n_mx_edi.view_l10n_mx_edi_ir_ui_view_form_inherit")
    util.remove_view(cr, "l10n_mx_edi.l10n_mx_edi_addenda_bosh_A_C")
    util.remove_view(cr, "l10n_mx_edi.l10n_mx_edi_addenda_autozone")
