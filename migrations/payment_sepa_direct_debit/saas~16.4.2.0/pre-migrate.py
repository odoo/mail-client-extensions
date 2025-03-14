from odoo.upgrade import util


def migrate(cr, version):
    fields_to_remove = {
        "payment.provider": ["sdd_sms_verification_required", "sdd_signature_required", "sdd_sms_credits"],
        "sdd.mandate": [
            "verified",
            "verification_code",
            "phone_number",
            "signature",
            "signed_by",
            "signed_on",
        ],
    }
    for model in fields_to_remove:
        fields = fields_to_remove[model]
        for field in fields:
            util.remove_field(cr, model, field)

    for view in ["sdd_mandate_form", "sdd_payment_mandate_form", "payment_provider_form"]:
        util.remove_view(cr, f"payment_sepa_direct_debit.{view}")

    cr.execute(
        """
       UPDATE payment_provider provider
           SET code='custom',
               custom_mode='sepa_direct_debit'
         WHERE provider.code='sepa_direct_debit'
        """
    )

    util.change_field_selection_values(cr, "payment.provider", "code", {"sepa_direct_debit": "custom"})
