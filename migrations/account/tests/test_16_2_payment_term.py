# -*- coding: utf-8 -*-
import unittest

from odoo import fields

from .test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@unittest.skip("Will be fixed by #4582")
@change_version("16.2")
class TestPaymentTerm(TestAccountingSetupCommon):
    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------
    def _prepare_test_migrate_prepare_payment_term(self):
        pt_30_percent_now_balance_7_days = self.env["account.payment.term"].create(
            {
                "name": "30% now, Balance 7 days",
                "line_ids": [
                    fields.Command.create(
                        {"value": "percent", "value_amount": 30, "days": 0},
                    ),
                    fields.Command.create(
                        {"value": "balance", "days": 7},
                    ),
                ],
            }
        )
        pt_50_percent_3_days_after_end_month_balance_2_months = self.env["account.payment.term"].create(
            {
                "name": "50 percent 3 days after the end of the month, balance in two months",
                "line_ids": [
                    fields.Command.create(
                        {"value": "percent", "value_amount": 50, "months": 1, "days": 3},
                    ),
                    fields.Command.create(
                        {"value": "balance", "months": 2},
                    ),
                ],
            }
        )
        self.env.user.company_id.early_pay_discount_computation = "mixed"
        pt_2_lines_2_epd = self.env["account.payment.term"].create(
            {
                "name": "50 percent in 5 days with 2% epd, 50 percent in 10 days with 5% epd",
                "company_id": self.env.user.company_id.id,
                "line_ids": [
                    fields.Command.create(
                        {
                            "value": "percent",
                            "value_amount": 50,
                            "days_after": 5,
                            "months": 2,
                            "discount_percentage": 2,
                            "discount_days": 5,
                        },
                    ),
                    fields.Command.create(
                        {
                            "value": "percent",
                            "value_amount": 50,
                            "days_after": 10,
                            "months": 1,
                            "discount_percentage": 5,
                            "discount_days": 10,
                        },
                    ),
                    fields.Command.create(
                        {"value": "balance", "days": 5},
                    ),
                ],
            }
        )
        pt_balance_7_days = self.env["account.payment.term"].create(
            {
                "name": "Balance 7 days",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 7},
                    ),
                ],
            }
        )
        return [
            pt_30_percent_now_balance_7_days.id,
            pt_50_percent_3_days_after_end_month_balance_2_months.id,
            pt_2_lines_2_epd.id,
            pt_balance_7_days.id,
        ]

    def _check_migrate_payment_term(self, config, pt_1, pt_2, pt_3, pt_4):
        pt_30_percent_now_balance_7_days = self.env["account.payment.term"].browse(pt_1)
        pt_50_percent_3_days_after_end_month_balance_2_months = self.env["account.payment.term"].browse(pt_2)
        pt_2_lines_2_epd = self.env["account.payment.term"].browse(pt_3)
        pt_balance_7_days = self.env["account.payment.term"].browse(pt_4)

        self.assertRecordValues(
            pt_30_percent_now_balance_7_days.line_ids.sorted(key=lambda ptl: ptl.value_amount),
            (
                {"value": "percent", "value_amount": 30, "delay_type": "days_after", "nb_days": 0},
                {"value": "percent", "value_amount": 70, "delay_type": "days_after", "nb_days": 7},
            ),
        )
        self.assertRecordValues(
            pt_50_percent_3_days_after_end_month_balance_2_months.line_ids.sorted(key=lambda ptl: ptl.id),
            (
                {"value": "percent", "value_amount": 50, "delay_type": "days_after_end_of_next_month", "nb_days": 5},
                {"value": "percent", "value_amount": 50, "delay_type": "days_after_end_of_month", "nb_days": 10},
            ),
        )
        self.assertTrue(pt_2_lines_2_epd.early_discount)
        self.assertEqual(pt_2_lines_2_epd.discount_percentage, 5.0)
        self.assertEqual(pt_2_lines_2_epd.discount_days, 10)
        self.assertEqual(pt_2_lines_2_epd.early_pay_discount_computation, "mixed")
        self.assertRecordValues(
            pt_balance_7_days.line_ids,
            {"value": "percent", "value_amount": 100, "delay_type": "days_after", "nb_days": 7},
        )

    def prepare(self):
        res = super().prepare()
        res["tests"].append(("_check_migrate_payment_term", self._prepare_test_migrate_prepare_payment_term()))
        return res
