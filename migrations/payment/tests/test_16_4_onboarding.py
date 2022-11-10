# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.onboarding.tests.test_common import UpgradeOnboardingCase
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~16.4")
class TestMoveOnboardings(UpgradeOnboardingCase):
    def prepare(self):
        test_companies = self.env["res.company"].create(
            [
                {
                    "name": f"Test Company Payment Onboarding Step {idx+1}",
                    "country_id": self.env.ref("base.be").id,
                    "payment_provider_onboarding_state": step_state,
                }
                for idx, step_state in enumerate(("done", "just_done", "not_done"))
            ]
        )

        return {"company_ids": test_companies.ids}

    def check(self, init):
        payment_provider_onboarding_step = self.env.ref("payment.onboarding_onboarding_step_payment_provider")
        companies = self.env["res.company"].browse(init["company_ids"])
        self._check_onboarding_step_completed(payment_provider_onboarding_step, companies[0])
        self._check_onboarding_step_completed(payment_provider_onboarding_step, companies[1])
        self._check_onboarding_step_not_completed(payment_provider_onboarding_step, companies[2])
