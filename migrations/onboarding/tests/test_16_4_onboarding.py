# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.onboarding.tests.test_common import UpgradeOnboardingCase
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~16.4")
class TestUpgradeOnboardings(UpgradeOnboardingCase):
    def prepare(self):
        company_1, company_2 = self.env["res.company"].create(
            [
                {
                    "name": f"Test Company Onboarding {idx+1}",
                    "country_id": self.env.ref("base.be").id,
                }
                for idx in range(2)
            ]
        )
        onboarding_1 = self.env["onboarding.onboarding"].create(
            {"name": "Test Onboarding 1", "is_per_company": True, "route_name": "onboarding1"}
        )
        step_1, step_2 = self.env["onboarding.onboarding.step"].create(
            [
                {
                    "title": f"Test Onboarding 1 - Step {idx+1}",
                    "onboarding_id": onboarding_1.id,
                    "panel_step_open_action_name": "action_fake_open_onboarding_step",
                }
                for idx in range(2)
            ]
        )

        onboarding_1.with_company(company_1)._search_or_create_progress()
        onboarding_1.with_company(company_2)._search_or_create_progress()
        (step_1 | step_2).with_company(company_1).action_set_just_done()
        step_1.with_company(company_2).action_set_just_done()
        onboarding_1.with_company(company_2).action_close()

        return {
            "company_ids": [company_1.id, company_2.id],
            "test_onboarding_1_id": onboarding_1.id,
            "test_onboarding_1_step_ids": [step_1.id, step_2.id],
        }

    def check(self, init):
        test_company_1, test_company_2 = self.env["res.company"].browse(init["company_ids"])
        test_onboarding_1 = self.env["onboarding.onboarding"].browse(init["test_onboarding_1_id"])
        step_1, step_2 = self.env["onboarding.onboarding.step"].browse(init["test_onboarding_1_step_ids"])

        # Check complete and open for company 1
        self._check_onboarding_completed(test_onboarding_1, test_company_1)
        self._check_onboarding_step_completed(step_1, test_company_1)
        self._check_onboarding_step_completed(step_2, test_company_1)
        self._check_onboarding_not_closed(test_onboarding_1, test_company_1)

        # Check incomplete and closed for company 2
        self._check_onboarding_not_completed(test_onboarding_1, test_company_2)
        self._check_onboarding_closed(test_onboarding_1, test_company_2)
        self._check_onboarding_step_completed(step_1, test_company_2)
        self._check_onboarding_step_not_completed(step_2, test_company_2)
