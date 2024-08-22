from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "account_consolidation.consolidation_chart_form_onboarding")
    util.remove_view(cr, "account_consolidation.consolidation_period_form_onboarding")
    util.remove_view(cr, "account_consolidation.consolidation_account_tree_onboarding")
    util.remove_record(cr, "account_consolidation.onboarding_onboarding_step_setup_consolidation")
    util.remove_record(cr, "account_consolidation.onboarding_onboarding_step_setup_ccoa")
    util.remove_record(cr, "account_consolidation.onboarding_onboarding_step_create_consolidation_period")
    util.remove_record(cr, "account_consolidation.onboarding_onboarding_account_consolidation_dashboard")
