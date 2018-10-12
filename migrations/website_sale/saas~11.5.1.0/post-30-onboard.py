# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        "UPDATE res_company SET website_sale_onboarding_payment_acquirer_state=payment_acquirer_onboarding_state"
    )
