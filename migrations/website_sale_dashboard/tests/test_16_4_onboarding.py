# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.onboarding.tests.test_common import UpgradeOnboardingCase
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~16.4")
class TestMoveOnboardings(UpgradeOnboardingCase):
    def prepare(self):
        test_companies = self.env["res.company"].create(
            [
                {
                    "name": f"Test Company Website Sale Dashboard Onboarding #{idx+1}",
                    "country_id": self.env.ref("base.be").id,
                    "base_onboarding_company_state": "done",
                    "payment_provider_onboarding_state": "just_done",
                    "account_onboarding_sale_tax_state": step_state,
                }
                for idx, step_state in enumerate(("done", "just_done", "not_done"))
            ]
        )

        return {"company_ids": test_companies.ids}

    def check(self, init):
        company_done, company_just_done, company_not_done = self.env["res.company"].browse(init["company_ids"])

        account_onboarding_sale_tax_step = self.env.ref("account.onboarding_onboarding_step_sales_tax")

        self._check_onboarding_step_completed(account_onboarding_sale_tax_step, company_done)
        self._check_onboarding_step_completed(account_onboarding_sale_tax_step, company_just_done)
        self._check_onboarding_step_not_completed(account_onboarding_sale_tax_step, company_not_done)

        website_sale_dashboard_onboarding = self.env.ref(
            "website_sale_dashboard.onboarding_onboarding_website_sale_dashboard"
        )

        self._check_onboarding_completed(website_sale_dashboard_onboarding, company_done)
        self._check_onboarding_completed(website_sale_dashboard_onboarding, company_just_done)
        self._check_onboarding_not_completed(website_sale_dashboard_onboarding, company_not_done)
