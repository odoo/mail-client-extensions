from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "payment_method", "support_manual_capture", "varchar", default="none")

    methods_to_update = {
        "full_only": ["affirm", "revolut_pay", "walley"],
        "partial": [
            "afterpay",
            "afterpay_riverty",
            "alma",
            "amazon_pay",
            "card",
            "cash_app_pay",
            "clearpay",
            "emi_india",
            "klarna",
            "klarna_paynow",
            "klarna_pay_over_time",
            "mobile_pay",
            "netbanking",
            "paybright",
            "paylater_india",
            "paypal",
            "paypay",
            "ratepay",
            "samsung_pay",
            "twint",
            "unknown",
            "vipps",
        ],
    }
    for support, xids in methods_to_update.items():
        ids = tuple(util.ref(cr, f"payment.payment_method_{suffix}") for suffix in xids)
        cr.execute("UPDATE payment_method SET support_manual_capture = %s WHERE id IN %s", [support, ids])
