# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations.onboarding.tests.test_common import UpgradeOnboardingCase
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~16.4")
class TestUpgradeAppointmentOnboardings(UpgradeOnboardingCase):
    def prepare(self):
        # Partially complete onboarding and close it
        onboarding = self.env.ref("appointment.appointment_onboarding_panel")
        steps = (
            self.env.ref("appointment.appointment_onboarding_create_appointment_type_step")
            | self.env.ref("appointment.appointment_onboarding_preview_invite_step")
            | self.env.ref("appointment.appointment_onboarding_configure_calendar_provider_step")
        )
        onboarding._search_or_create_progress()
        steps[:2].action_set_just_done()
        onboarding.action_close()
        self._check_completion(onboarding, steps)

        return {"panel_id": onboarding.id, "step_ids": steps.ids}

    def check(self, init):
        onboarding = self.env["onboarding.onboarding"].browse(init["panel_id"])
        steps = self.env["onboarding.onboarding.step"].browse(init["step_ids"])
        self._check_completion(onboarding, steps)

    def _check_completion(self, onboarding, steps):
        # Check incomplete but closed onboarding
        self._check_onboarding_not_completed(onboarding, self.env.company)
        self._check_onboarding_closed(onboarding, self.env.company)

        self._check_onboarding_step_completed(steps[0], self.env.company)
        self._check_onboarding_step_completed(steps[1], self.env.company)
        self._check_onboarding_step_not_completed(steps[2], self.env.company)
