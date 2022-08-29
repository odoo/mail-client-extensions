from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_custom.transfer_transaction_status", "payment_custom.custom_transaction_status")

    util.create_column(cr, "payment_acquirer", "custom_mode", "varchar")

    cr.execute(
        """
            UPDATE payment_acquirer
               SET provider = 'custom',
                   custom_mode = 'transfer'
             WHERE provider = 'transfer'
        """
    )
