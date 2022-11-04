from odoo.upgrade import util


def migrate(cr, version):
    util.rename_model(cr, "payment.icon", "payment.method")

    util.rename_field(cr, "payment.provider", "payment_icon_ids", "payment_method_ids")
    util.rename_field(cr, "payment.provider", "show_payment_icon_ids", "show_payment_method_ids")

    cr.execute(
        """
        ALTER TABLE payment_icon_payment_provider_rel
          RENAME TO payment_method_payment_provider_rel
    """
    )
    cr.execute(
        """
        ALTER TABLE payment_method_payment_provider_rel
      RENAME COLUMN payment_icon_id
                 TO payment_method_id
    """
    )

    eb = util.expand_braces

    util.rename_xmlid(cr, *eb("payment.action_payment_{icon,method}"))

    for method in (
        "paypal",
        "apple_pay",
        "sepa",
        "kbc",
        "mpesa",
        "airtel_money",
        "mtn_mobile_money",
        "barter_by_flutterwave",
        "sadad",
        "mada",
        "bbva_bancomer",
        "citibanamex",
        "cc_visa",
        "cc_mastercard",
        "cc_american_express",
        "cc_discover",
        "cc_diners_club_intl",
        "cc_rupay",
        "cc_jcb",
        "cc_maestro",
        "cc_cirrus",
        "cc_unionpay",
        "cc_bancontact",
        "cc_western_union",
        "cc_ideal",
        "cc_webmoney",
        "cc_giropay",
        "cc_eps",
        "cc_p24",
        "cc_codensa_easy_credit",
    ):
        util.rename_xmlid(cr, f"payment.payment_icon_{method}", f"payment.payment_method_{method.replace('cc_', '')}")

    util.rename_xmlid(cr, *eb("payment.payment_{icon,method}_form"))
    util.rename_xmlid(cr, *eb("payment.payment_{icon,method}_tree"))

    util.rename_xmlid(cr, *eb("payment.payment_{icon,method}_all"))
    util.rename_xmlid(cr, *eb("payment.payment_{icon,method}_system"))

    # Setting default name for already existing payment methodss without name
    cr.execute(
        """
        UPDATE payment_method
           SET name = 'Payment Method Name'
         WHERE name IS NULL
        """
    )

    # Removes payment methods that did not have image
    cr.execute(
        """
        DELETE FROM payment_method pm
        WHERE NOT EXISTS (SELECT *
                            FROM ir_attachment ia
                           WHERE pm.id = ia.res_id
                             AND ia.res_model = 'payment.method'
                             AND ia.res_field = 'image'
        )
        """
    )
