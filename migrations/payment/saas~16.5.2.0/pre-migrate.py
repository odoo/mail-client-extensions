from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "payment.provider", "fees_active")
    util.remove_field(cr, "payment.provider", "fees_dom_fixed")
    util.remove_field(cr, "payment.provider", "fees_dom_var")
    util.remove_field(cr, "payment.provider", "fees_int_fixed")
    util.remove_field(cr, "payment.provider", "fees_int_var")
    util.remove_field(cr, "payment.provider", "support_fees")
    util.remove_field(cr, "payment.provider", "display_as")
    util.remove_field(cr, "payment.provider", "show_payment_method_ids")
    util.remove_field(cr, "payment.transaction", "fees")
    util.remove_field(cr, "payment.token", "verified")
    util.remove_field(cr, "payment.link.wizard", "available_provider_ids")
    util.remove_field(cr, "payment.link.wizard", "has_multiple_providers")
    util.remove_field(cr, "payment.link.wizard", "payment_provider_selection")
    util.remove_field(cr, "payment.link.wizard", "description")

    util.remove_view(cr, "payment.checkout")
    util.remove_view(cr, "payment.manage")
    util.remove_view(cr, "payment.icon_list")
    util.remove_view(cr, "payment.verified_token_checkmark")
    util.remove_view(cr, "payment.test_token_badge")
    util.remove_view(cr, "payment.footer")

    util.rename_xmlid(cr, "payment.payment_method_kbc", "payment.payment_method_kbc_cbc")
    util.rename_xmlid(cr, "payment.payment_method_codensa_easy_credit", "payment.payment_method_codensa")
    util.rename_xmlid(cr, "payment.payment_method_sepa", "payment.payment_method_sepa_direct_debit")
    util.rename_xmlid(cr, "payment.payment_method_diners_club_intl", "payment.payment_method_diners")
    util.rename_xmlid(cr, "payment.payment_method_american_express", "payment.payment_method_amex")
    util.update_record_from_xml(cr, "payment.payment_method_upi")
