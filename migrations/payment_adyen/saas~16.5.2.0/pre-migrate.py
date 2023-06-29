from odoo.upgrade import util


def migrate(cr, version):

    util.remove_view(cr, "payment_adyen.checkout")
    util.remove_view(cr, "payment_adyen.manage")
    util.remove_view(cr, "payment_adyen.sdk_assets")

    util.remove_field(cr, "payment.provider", "adyen_recurring_api_url")
    util.rename_field(cr, "payment.provider", "adyen_checkout_api_url", "adyen_api_url_prefix")
    cr.execute(
        r"""
       UPDATE payment_provider
          SET adyen_api_url_prefix = (regexp_match(adyen_api_url_prefix, '(?:https://)?(\w+-\w+).*'))[1]
        WHERE code = 'adyen'
        """
    )
