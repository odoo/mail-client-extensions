# -*- coding: utf-8 -*-

from odoo.upgrade import util

onboarding_utils = util.import_script("onboarding/saas~16.4.1.2/pre-migrate.py")


def migrate(cr, version):
    onboarding_utils.migrate_onboarding(cr, ONBOARDING_MIGRATION_PARAMS, remove_step_fields_for_module=False)


ONBOARDING_MIGRATION_PARAMS = {
    "website_sale_dashboard_onboarding": {
        "state_field": "website_sale_dashboard_onboarding_state",
        "id": "website_sale_dashboard.onboarding_onboarding_website_sale_dashboard",
        "steps": [
            (
                "base_onboarding_company_state",
                "account.onboarding_onboarding_step_company_data",
            ),
            (
                "payment_provider_onboarding_state",
                "website_sale_dashboard.onboarding_onboarding_step_payment_provider",
            ),
            (
                "account_onboarding_sale_tax_state",
                "account.onboarding_onboarding_step_sales_tax",
            ),
        ],
    }
}
