from odoo.upgrade import util


def migrate(cr, version):

    # === PAYMENT ACQUIRER === #

    util.update_record_from_xml(cr, "payment.payment_acquirer_odoo")
    util.update_record_from_xml(cr, "payment.payment_acquirer_ogone")

    # === PAYMENT ICON === #
    Icon = util.env(cr)["payment.icon"]
    for icon in util.iter_browse(Icon, Icon.search([]).ids):
        icon.image = icon.image  # Resize the images after changing the field from Binary to Image

    # === IR CRON === #
    util.update_record_from_xml(cr, "payment.cron_post_process_payment_tx")

    # === IR RULE === #
    util.update_record_from_xml(cr, "payment.payment_transaction_user_rule")
    util.update_record_from_xml(cr, "payment.payment_token_user_rule")
    util.update_record_from_xml(cr, "payment.payment_transaction_billing_rule")
    util.update_record_from_xml(cr, "payment.payment_token_billing_rule")
