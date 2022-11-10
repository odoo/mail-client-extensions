# -*- coding: utf-8 -*-

from odoo.upgrade import util

onboarding_utils = util.import_script("onboarding/saas~16.4.1.2/pre-migrate.py")


def migrate(cr, version):
    onboarding_utils.migrate_standalone_onboarding_steps(
        cr, ONBOARDING_MIGRATION_PARAMS, remove_step_fields_for_module=False
    )


ONBOARDING_MIGRATION_PARAMS = {
    "payment_provider_onboarding": {
        "id": None,
        "state_field": None,
        "steps": [
            (
                "payment_provider_onboarding_state",
                "payment.onboarding_onboarding_step_payment_provider",
            ),
        ],
    }
}
