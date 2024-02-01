# -*- coding: utf-8 -*-

# old-style import because this script is imported for tests
from odoo.addons.base.maintenance.migrations import util

onboarding_utils = util.import_script("onboarding/saas~16.4.1.2/pre-migrate.py")


def migrate(cr, version):
    # Some states are used in other onboardings (other modules), so we'll remove them in `end-`.
    onboarding_utils.migrate_onboarding(cr, ONBOARDING_MIGRATION_PARAMS, remove_step_fields_for_module=False)

    util.remove_field(cr, "res.company", "account_onboarding_create_invoice_state")  # only _flag was stored data

    onboarding_utils.migrate_standalone_onboarding_steps(
        cr,
        ONBOARDING_MIGRATION_PARAMS_STANDALONE_STEPS,
        remove_step_fields_for_module=False,
    )

    # Now an onboarding.onboarding.step model method
    util.remove_record(cr, "account.action_open_account_onboarding_sale_tax")
    rules_to_update = [
        "account.journal_comp_rule",
        "account.account_comp_rule",
        "account.journal_group_comp_rule",
        "account.account_group_comp_rule",
        "account.account_root_comp_rule",
        "account.tax_group_comp_rule",
        "account.tax_comp_rule",
        "account.tax_rep_comp_rule",
        "account.account_fiscal_position_comp_rule",
        "account.account_reconcile_model_template_comp_rule",
        "account.account_reconcile_model_line_template_comp_rule",
    ]
    for rule in rules_to_update:
        util.if_unchanged(cr, rule, util.update_record_from_xml)


ONBOARDING_MIGRATION_PARAMS = {
    "invoice_onboarding": {
        "state_field": "account_invoice_onboarding_state",
        "id": "account.onboarding_onboarding_account_invoice",
        "steps": [
            (
                "base_onboarding_company_state",
                "account.onboarding_onboarding_step_company_data",
            ),
            (
                "account_onboarding_invoice_layout_state",
                "account.onboarding_onboarding_step_base_document_layout",
            ),
            (
                "account_onboarding_create_invoice_state_flag",
                "account.onboarding_onboarding_step_create_invoice",
            ),
        ],
    },
    "dashboard_onboarding": {
        "state_field": "account_dashboard_onboarding_state",
        "id": "account.onboarding_onboarding_account_dashboard",
        "steps": (
            (
                "account_setup_bank_data_state",
                "account.onboarding_onboarding_step_bank_account",
            ),
            (
                "account_setup_fy_data_state",
                "account.onboarding_onboarding_step_fiscal_year",
            ),
            (
                "account_setup_coa_state",
                "account.onboarding_onboarding_step_chart_of_accounts",
            ),
            (
                "account_setup_taxes_state",
                "account.onboarding_onboarding_step_default_taxes",
            ),
        ),
    },
}

ONBOARDING_MIGRATION_PARAMS_STANDALONE_STEPS = {
    "account_extra_steps": {
        "state_field": None,
        "id": None,
        "steps": [
            (
                "account_setup_bill_state",
                "account.onboarding_onboarding_step_setup_bill",
            ),
            (
                "account_onboarding_sale_tax_state",
                "account.onboarding_onboarding_step_sales_tax",
            ),
        ],
    }
}
