from odoo.upgrade import util


def migrate(cr, version):
    script = util.import_script("l10n_in/saas~18.2.2.0/pre-migrate.py")
    script._l10n_in_enable_feature(cr, "l10n_in_edi_feature")
    util.remove_field(cr, "account.move", "l10n_in_edi_show_cancel")
    util.create_column(cr, "account_move", "l10n_in_edi_status", "varchar")
    util.create_column(cr, "account_move", "l10n_in_edi_error", "varchar")
    cr.execute(
        """
        UPDATE account_move AS move
           SET l10n_in_edi_status = CASE
                  WHEN aed.state = 'to_cancel' THEN 'sent'
                  ELSE aed.state
               END,
               l10n_in_edi_error = aed.error
          FROM account_edi_document AS aed
          JOIN account_edi_format AS aef
            ON aed.edi_format_id = aef.id
         WHERE move.id = aed.move_id
           AND aef.code = 'in_einvoice_1_03'
        """
    )
    cr.execute(
        """
        UPDATE ir_attachment a
           SET res_field = 'l10n_in_edi_attachment_file'
          FROM account_edi_document aed
          JOIN account_edi_format aef
            ON aed.edi_format_id = aef.id
         WHERE a.id = aed.attachment_id
           AND aef.code = 'in_einvoice_1_03'
        """
    )
    cr.execute("""
        DELETE FROM account_edi_document aed
              USING account_edi_format aef
              WHERE aef.code = 'in_einvoice_1_03'
                AND aef.id = aed.edi_format_id
    """)
    util.delete_unused(cr, "l10n_in.edi_in_einvoice_json_1_03")
