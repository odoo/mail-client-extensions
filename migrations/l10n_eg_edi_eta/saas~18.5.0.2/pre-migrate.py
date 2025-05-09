from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        UPDATE ir_attachment att
           SET res_field = 'l10n_eg_eta_json_doc_file'
          FROM account_move move
         WHERE att.id = move.l10n_eg_eta_json_doc_id
        """
    )

    util.remove_field(cr, "account.move", "l10n_eg_eta_json_doc_id")
