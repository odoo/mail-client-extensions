from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "payment_custom.payment_acquirer_form", "payment_custom.payment_provider_form")
    util.rename_xmlid(cr, "payment_custom.transfer_transaction_status", "payment_custom.custom_transaction_status")

    util.create_column(cr, "payment_provider", "custom_mode", "varchar")
    cr.execute(
        """
            UPDATE payment_provider
               SET custom_mode = 'wire_transfer'
             WHERE code = 'transfer'
        """
    )

    util.change_field_selection_values(cr, "payment.provider", "code", {"transfer": "custom"})
