from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.provider", "currency_id")
    util.rename_xmlid(
        cr, "payment_sepa_direct_debit.payment_acquirer_kanban", "payment_sepa_direct_debit.payment_provider_kanban"
    )
    util.rename_xmlid(
        cr, "payment_sepa_direct_debit.payment_acquirer_form", "payment_sepa_direct_debit.payment_provider_form"
    )
