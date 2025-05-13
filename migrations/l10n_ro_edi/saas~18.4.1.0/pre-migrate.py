from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
            UPDATE ir_attachment ia
               SET res_id = rd.id,
                   res_model = 'l10n_ro_edi.document',
                   res_field = 'attachment'
              FROM l10n_ro_edi_document rd
             WHERE ia.id = rd.attachment_id
        """,
        table="ir_attachment",
        alias="ia",
    )
    util.change_field_selection_values(
        cr, "l10n_ro_edi.document", "state", {"invoice_sending_failed": "invoice_refused"}
    )
    util.remove_field(cr, "l10n_ro_edi.document", "key_loading")
    util.remove_field(cr, "l10n_ro_edi.document", "attachment_id")
    util.remove_field(cr, "account.move", "l10n_ro_edi_attachment_id")
