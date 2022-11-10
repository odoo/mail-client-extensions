# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.onboarding.tests.test_common import UpgradeOnboardingCase
from odoo.addons.base.maintenance.migrations.testing import change_version

post_migrate = util.import_script("account/saas~16.4.1.2/post-migrate.py")


@change_version("saas~16.4")
class TestMoveOnboardings(UpgradeOnboardingCase):
    def prepare(self):
        test_company_1, test_company_2 = self.env["res.company"].create(
            [
                {
                    "name": f"Test Company Move Account Onboarding {idx+1}",
                    "country_id": self.env.ref("base.be").id,
                }
                for idx in range(2)
            ]
        )

        # Complete invoicing onboarding (closed with closed state),
        # and part of dashboard in company 1 (closed with closed state)
        test_company_1.write(
            {
                # Invoicing
                "base_onboarding_company_state": "done",
                "account_onboarding_invoice_layout_state": "just_done",
                "account_onboarding_create_invoice_state_flag": True,
                "account_invoice_onboarding_state": "closed",
                # Dashboard
                "account_setup_bank_data_state": "done",
                "account_setup_fy_data_state": "done",
                "account_dashboard_onboarding_state": "closed",
                "account_setup_bill_state": "done",
            }
        )

        # Complete dashboard onboarding (closed because was always hidden when done),
        # the sale tax step which is only on website_sale_dashboard panel now,
        # and part of invoicing in company 2 (not closed)
        test_company_2.write(
            {
                # Invoicing
                "base_onboarding_company_state": "done",
                "account_onboarding_invoice_layout_state": "done",
                "account_setup_bank_data_state": "done",
                # Dashboard
                "account_setup_fy_data_state": "done",
                "account_setup_coa_state": "done",
                "account_setup_taxes_state": "done",
                "account_dashboard_onboarding_state": "done",
                # Standalone / Website Sale Dashboard
                "account_onboarding_sale_tax_state": "done",
            }
        )

        return {"company_ids": [test_company_1.id, test_company_2.id]}

    def check(self, init):
        test_company_1, test_company_2 = self.env["res.company"].browse(init["company_ids"])

        onboarding_data = post_migrate.ONBOARDING_MIGRATION_PARAMS

        account_invoice_onboarding = self.env.ref(onboarding_data["invoice_onboarding"]["id"])
        account_dashboard_onboarding_panel = self.env.ref(onboarding_data["dashboard_onboarding"]["id"])

        # As we bypassed ORM methods, make sure to mark this step as done if it was added (account_payment).
        account_payment_onboarding_provider_step = self.env.ref(
            "account_payment.onboarding_onboarding_step_payment_provider", raise_if_not_found=False
        )
        if account_payment_onboarding_provider_step:
            account_payment_onboarding_provider_step.with_company(test_company_1).action_set_just_done()
            account_payment_onboarding_provider_step.with_company(
                test_company_1
            ).current_progress_step_id.flush_recordset()
            account_invoice_onboarding.with_company(test_company_1).current_progress_id._recompute_progress_step_ids()

        # Check complete invoicing onboarding and part of dashboard in company 1
        self._check_onboarding_completed(account_invoice_onboarding, test_company_1)
        self._check_onboarding_closed(account_invoice_onboarding, test_company_1)

        self._check_onboarding_not_completed(account_dashboard_onboarding_panel, test_company_1)
        self._check_onboarding_closed(account_dashboard_onboarding_panel, test_company_1)

        # Check dashboard onboarding and part of invoicing in company 2
        self._check_onboarding_completed(account_dashboard_onboarding_panel, test_company_2)
        self._check_onboarding_closed(account_dashboard_onboarding_panel, test_company_2)

        self._check_onboarding_not_completed(account_invoice_onboarding, test_company_2)
        self._check_onboarding_not_closed(account_invoice_onboarding, test_company_2)

        setup_bill_step = self.env.ref("account.onboarding_onboarding_step_setup_bill")
        self._check_onboarding_step_completed(setup_bill_step, test_company_1)
        self._check_onboarding_step_not_completed(setup_bill_step, test_company_2)

        sale_tax_step = self.env.ref("account.onboarding_onboarding_step_sales_tax")
        self._check_onboarding_step_not_completed(sale_tax_step, test_company_1)
        self._check_onboarding_step_completed(sale_tax_step, test_company_2)
