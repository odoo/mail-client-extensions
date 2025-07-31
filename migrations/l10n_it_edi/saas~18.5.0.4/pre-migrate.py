from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "account_move", "l10n_it_edi_attachment_name", "varchar")

    query = """
        UPDATE account_move
           SET l10n_it_edi_attachment_name = ir_attachment.name
          FROM ir_attachment
         WHERE account_move.id = ir_attachment.res_id
           AND ir_attachment.res_model = 'account.move'
           AND ir_attachment.res_field = 'l10n_it_edi_attachment_file'
    """
    util.explode_execute(cr, query, table="account_move")

    util.remove_field(cr, "account.move", "l10n_it_edi_attachment_id")

    util.remove_view(cr, "l10n_it_edi.account_invoice_it_FatturaPA_export_withholding")
    util.remove_view(cr, "l10n_it_edi.account_view_tax_form_l10n_it_edi_extended")
    util.remove_view(cr, "l10n_it_edi.view_invoice_tree_l10n_it_edi_extended")
