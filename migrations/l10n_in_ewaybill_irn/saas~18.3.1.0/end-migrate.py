# Run in end- as l10n_in_ewaybill records are created in saas~18.1.2.0 end-migration.
from odoo.upgrade import util


def migrate(cr, version):
    util.explode_execute(
        cr,
        """
        UPDATE l10n_in_ewaybill eb
           SET is_sent_through_irn = True
          FROM account_move AS am
         WHERE eb.account_move_id = am.id
           AND am.move_type != 'out_refund'
           AND am.debit_origin_id IS NULL
           AND am.l10n_in_edi_status = 'sent'
        """,
        table="l10n_in_ewaybill",
        alias="eb",
    )
