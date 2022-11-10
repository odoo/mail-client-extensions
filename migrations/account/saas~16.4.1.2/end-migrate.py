# -*- coding: utf-8 -*-

from odoo.upgrade import util

onboarding_utils = util.import_script("onboarding/saas~16.4.1.2/pre-migrate.py")
post_migrate = util.import_script("account/saas~16.4.1.2/post-migrate.py")


def migrate(cr, version):
    onboarding_utils.remove_onboarding_step_state_fields(cr, post_migrate.ONBOARDING_MIGRATION_PARAMS, "account")

    # Deleting now as might have been required for website_sale_dashboard
    onboarding_utils.remove_onboarding_step_state_fields(
        cr, post_migrate.ONBOARDING_MIGRATION_PARAMS_STANDALONE_STEPS, "account"
    )
