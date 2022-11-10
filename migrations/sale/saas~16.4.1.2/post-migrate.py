# -*- coding: utf-8 -*-

from odoo.upgrade import util

onboarding_utils = util.import_script("onboarding/saas~16.4.1.2/pre-migrate.py")


def migrate(cr, version):
    # account steps may be reused, so only deleting sale ones.
    onboarding_utils.migrate_onboarding(cr, ONBOARDING_MIGRATION_PARAMS, remove_step_fields_for_module="sale")


ONBOARDING_MIGRATION_PARAMS = {
    "sale_quotation_onboarding": {
        "state_field": "sale_quotation_onboarding_state",
        "id": "sale.onboarding_onboarding_sale_quotation",
        "steps": [
            (
                "base_onboarding_company_state",
                "account.onboarding_onboarding_step_company_data",
            ),
            (
                "account_onboarding_invoice_layout_state",
                "account.onboarding_onboarding_step_base_document_layout",
            ),
            (
                "sale_onboarding_order_confirmation_state",
                "sale.onboarding_onboarding_step_sale_order_confirmation",
            ),
            (
                "sale_onboarding_sample_quotation_state",
                "sale.onboarding_onboarding_step_sample_quotation",
            ),
        ],
    },
}
