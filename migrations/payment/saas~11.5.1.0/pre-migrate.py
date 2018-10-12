# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "qr_code", "boolean")

    util.create_column(cr, "payment_transaction", "return_url", "varchar")
    util.create_column(cr, "payment_transaction", "is_processed", "boolean")
    cr.execute("UPDATE payment_transaction SET is_processed=true")

    util.create_column(cr, "res_company", "payment_acquirer_onboarding_state", "varchar")
    util.create_column(cr, "res_company", "payment_onboarding_payment_method", "varchar")

    cr.execute("""
        UPDATE res_company
           SET payment_acquirer_onboarding_state =
                CASE WHEN id IN (select company_id
                                   from account_payment
                                  where payment_transaction_id is not null
                               group by company_id)
                     THEN 'just_done'
                     ELSE 'not_done'
                 END
    """)
