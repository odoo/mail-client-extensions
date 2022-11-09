# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase

onboarding_utils = util.import_script("onboarding/saas~16.4.1.2/pre-migrate.py")


class UpgradeOnboardingCase(UpgradeCase, abstract=True):
    """
    UpgradeCase with methods to check the progress of onboardings (to saas~16.4).
    """

    def _check_onboarding_completed(self, onboarding, company):
        self.assertTrue(self.is_onboarding_completed(onboarding, company))

    def _check_onboarding_not_completed(self, onboarding, company):
        self.assertFalse(self.is_onboarding_completed(onboarding, company))

    def _check_onboarding_closed(self, onboarding, company):
        self.assertTrue(self.is_onboarding_closed(onboarding, company))

    def _check_onboarding_not_closed(self, onboarding, company):
        self.assertFalse(self.is_onboarding_closed(onboarding, company))

    def _check_onboarding_step_completed(self, onboarding_step, company):
        self.assertTrue(self.is_onboarding_step_completed(onboarding_step, company))

    def _check_onboarding_step_not_completed(self, onboarding_step, company):
        self.assertFalse(self.is_onboarding_step_completed(onboarding_step, company))

    @staticmethod
    def is_onboarding_completed(onboarding, company):
        return onboarding.with_company(company).current_onboarding_state in {"done", "just_done"}

    @staticmethod
    def is_onboarding_step_completed(onboarding_step, company):
        return onboarding_step.with_company(company).current_step_state in {"done", "just_done"}

    @staticmethod
    def is_onboarding_closed(onboarding, company):
        return onboarding.with_company(company).is_onboarding_closed

    @staticmethod
    def convert_refs_to_ids(cr, onboarding_data):
        return onboarding_utils._convert_refs_to_ids(cr, onboarding_data)
