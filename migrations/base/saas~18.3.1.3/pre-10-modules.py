from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(
        cr, "website_sale_shiprocket.shiprocket_payment_method_cash_on_delivery", deactivate=True, keep_xmlids=False
    )
    util.delete_unused(
        cr, "website_sale_shiprocket.payment_provider_shiprocket_cod", deactivate=True, keep_xmlids=False
    )
    util.remove_module(cr, "website_sale_shiprocket")

    # Remove jitsi related modules:
    util.remove_inherit_from_model(cr, "event.sponsor", "chat.room.mixin")
    util.remove_module(cr, "website_event_jitsi")
    util.remove_module(cr, "website_event_meet")
    util.remove_module(cr, "website_event_meet_quiz")
    util.remove_module(cr, "website_jitsi")
    util.remove_module(cr, "l10n_in_purchase")

    util.rename_module(cr, "pos_viva_wallet", "pos_viva_com")
