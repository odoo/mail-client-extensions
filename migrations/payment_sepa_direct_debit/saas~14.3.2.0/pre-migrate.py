from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces

    # === PAYMENT ACQUIRER === #

    util.rename_field(cr, "payment.acquirer", "sepa_direct_debit_sms_enabled", "sdd_sms_verification_required")
    util.rename_field(cr, "payment.acquirer", "sepa_direct_debit_sign_enabled", "sdd_signature_required")
    util.rename_field(cr, "payment.acquirer", "iap_sms_credits", "sdd_sms_credits")

    # === IR UI VIEW === #

    util.remove_view(cr, xml_id="payment_sepa_direct_debit.sepa_direct_debit_form")
    util.remove_view(cr, xml_id="payment_sepa_direct_debit.sdd_payment_mandate_form")

    util.rename_xmlid(cr, *eb("payment_sepa_direct_debit.payment_acquirer_form{_sepa_direct_debit,}"))
    util.rename_xmlid(cr, *eb("payment_sepa_direct_debit.payment_acquirer_kanban{_sepa_direct_debit,}"))
    util.rename_xmlid(cr, *eb("payment_sepa_direct_debit.{payment_sepa_direct_debit,sdd}_mandate_form"))
