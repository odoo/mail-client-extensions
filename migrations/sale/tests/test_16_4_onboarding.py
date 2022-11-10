# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.onboarding.tests.test_common import UpgradeOnboardingCase
from odoo.addons.base.maintenance.migrations.testing import change_version

post_migrate = util.import_script("sale/saas~16.4.1.2/post-migrate.py")


@change_version("saas~16.4")
class TestMoveOnboardings(UpgradeOnboardingCase):
    def prepare(self):
        test_companies = self.env["res.company"].create(
            [
                {
                    "name": f"Test Company Sale Quotation Onboarding #{idx+1}",
                    "country_id": self.env.ref("base.be").id,
                }
                for idx in range(4)
            ]
        )

        # Complete onboarding (closed with closed state) in company 1
        test_companies[0].write(
            {
                "name": "Test Company Sale Quotation Onboarding 1",
                "sale_quotation_onboarding_state": "closed",
                "base_onboarding_company_state": "done",
                "account_onboarding_invoice_layout_state": "done",
                "sale_onboarding_order_confirmation_state": "done",
                "sale_onboarding_sample_quotation_state": "done",
            }
        )
        # Complete onboarding (closed by done state) in company 2
        test_companies[1].write(
            {
                "name": "Test Company Sale Quotation Onboarding 2",
                "sale_quotation_onboarding_state": "done",
                "base_onboarding_company_state": "done",
                "account_onboarding_invoice_layout_state": "done",
                "sale_onboarding_order_confirmation_state": "done",
                "sale_onboarding_sample_quotation_state": "done",
            }
        )
        # Incomplete onboarding (closed by closed state) in company 3
        test_companies[2].write(
            {
                "name": "Test Company Sale Quotation Onboarding 3",
                "sale_quotation_onboarding_state": "closed",
                "sale_onboarding_sample_quotation_state": "done",
            }
        )
        # Incomplete onboarding (not closed) in company 4
        test_companies[3].write(
            {
                "name": "Test Company Sale Quotation Onboarding 4",
                "sale_quotation_onboarding_state": "not_done",
                "base_onboarding_company_state": "done",
            }
        )
        return {"company_ids": test_companies.ids}

    def check(self, init):
        company_1, company_2, company_3, company_4 = self.env["res.company"].browse(init["company_ids"])

        sale_quotation_onboarding = self.env.ref(
            post_migrate.ONBOARDING_MIGRATION_PARAMS["sale_quotation_onboarding"]["id"]
        )

        # Check complete invoicing onboarding and part of dashboard in company 1
        self._check_onboarding_completed(sale_quotation_onboarding, company_1)
        self._check_onboarding_completed(sale_quotation_onboarding, company_2)
        self._check_onboarding_not_completed(sale_quotation_onboarding, company_3)
        self._check_onboarding_not_completed(sale_quotation_onboarding, company_4)

        self._check_onboarding_closed(sale_quotation_onboarding, company_1)
        self._check_onboarding_closed(sale_quotation_onboarding, company_2)
        self._check_onboarding_closed(sale_quotation_onboarding, company_3)
        self._check_onboarding_not_closed(sale_quotation_onboarding, company_4)
