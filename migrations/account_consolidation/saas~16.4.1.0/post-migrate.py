from odoo.upgrade import util

onboarding_utils = util.import_script("onboarding/saas~16.4.1.2/pre-migrate.py")


def migrate(cr, version):
    onboarding_utils.migrate_onboarding(cr, ONBOARDING_MIGRATION_PARAMS)


ONBOARDING_MIGRATION_PARAMS = {
    "consolidation_dashboard_onboarding": {
        "state_field": "consolidation_dashboard_onboarding_state",
        "id": "account_consolidation.onboarding_onboarding_account_consolidation_dashboard",
        "steps": [
            (
                "consolidation_setup_consolidation_state",
                "account_consolidation.onboarding_onboarding_step_setup_consolidation",
            ),
            (
                "consolidation_setup_ccoa_state",
                "account_consolidation.onboarding_onboarding_step_setup_ccoa",
            ),
            (
                "consolidation_create_period_state",
                "account_consolidation.onboarding_onboarding_step_create_consolidation_period",
            ),
        ],
    },
}
