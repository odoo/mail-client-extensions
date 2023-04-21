# -*- coding: utf-8 -*-

from odoo import fields

from .test_common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


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
                    fields.Command.create({"value": "percent", "value_amount": 30, "days": 0}),
                    fields.Command.create({"value": "balance", "days": 7}),
                ],
            }
        )
        pt_50_percent_3_days_after_end_month_balance_2_months = self.env["account.payment.term"].create(
            {
                "name": "50 percent 3 days after the end of the month, balance in two months",
                "line_ids": [
                    fields.Command.create(
                        {
                            "value": "percent",
                            "value_amount": 50,
                            "days": 1,
                            "months": 1,
                            "end_month": True,
                            "days_after": 3,
                        }
                    ),
                    fields.Command.create({"value": "balance", "days": 0, "months": 2}),
                ],
            }
        )
        self.env.company.early_pay_discount_computation = "mixed"
        pt_2_lines_2_epd = self.env["account.payment.term"].create(
            {
                "name": "50 percent in 5 days with 2% epd, 50 percent in 10 days with 5% epd",
                "company_id": self.env.company.id,
                "line_ids": [
                    fields.Command.create(
                        {
                            "value": "percent",
                            "value_amount": 50,
                            "days": 5,
                            "discount_percentage": 2,
                            "discount_days": 5,
                        }
                    ),
                    fields.Command.create(
                        {
                            "value": "balance",
                            "days": 10,
                            "discount_percentage": 5,
                            "discount_days": 10,
                        }
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
        pt_balance_0_days_0_months_eom_false = self.env["account.payment.term"].create(
            {
                "name": "Balance in_0_days_0_months",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 0},
                    ),
                ],
            }
        )
        pt_balance_0_days_0_months_eom_true = self.env["account.payment.term"].create(
            {
                "name": "Balance in_0_days_0_months, end_month --> true",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 0, "end_month": True},
                    ),
                ],
            }
        )
        pt_balance_0_days_1_months_eom_false = self.env["account.payment.term"].create(
            {
                "name": "Balance in 0 days 1 months",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 0, "months": 1},
                    ),
                ],
            }
        )
        pt_balance_0_days_1_months_eom_true = self.env["account.payment.term"].create(
            {
                "name": "Balance in 0 days 1 months end of month true",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 0, "months": 1, "end_month": True},
                    ),
                ],
            }
        )
        pt_balance_15_days_2_months_eom_false = self.env["account.payment.term"].create(
            {
                "name": "Balance in 15 days 2 months",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 15, "months": 2},
                    ),
                ],
            }
        )
        pt_balance_15_days_2_months_eom_true = self.env["account.payment.term"].create(
            {
                "name": "Balance in 15 days 2 months, end of month True",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 15, "months": 2, "end_month": True},
                    ),
                ],
            }
        )
        pt_balance_15_days_2_months_eom_true_10_days_after = self.env["account.payment.term"].create(
            {
                "name": "Balance in 15 days 2 months, 10 days after end of month",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 15, "months": 2, "end_month": True, "days_after": 10},
                    ),
                ],
            }
        )
        pt_balance_5_days_3_months_eom_true_6_days_after = self.env["account.payment.term"].create(
            {
                "name": "Balance in 5 days 3 months, 6 days after end of month",
                "line_ids": [
                    fields.Command.create(
                        {"value": "balance", "days": 5, "months": 3, "end_month": True, "days_after": 6},
                    ),
                ],
            }
        )
        return [
            (
                pt_30_percent_now_balance_7_days
                + pt_50_percent_3_days_after_end_month_balance_2_months
                + pt_2_lines_2_epd
                + pt_balance_7_days
                + pt_balance_0_days_0_months_eom_false
                + pt_balance_0_days_0_months_eom_true
                + pt_balance_0_days_1_months_eom_false
                + pt_balance_0_days_1_months_eom_true
                + pt_balance_15_days_2_months_eom_false
                + pt_balance_15_days_2_months_eom_true
                + pt_balance_15_days_2_months_eom_true_10_days_after
                + pt_balance_5_days_3_months_eom_true_6_days_after
            ).ids,
        ]

    def _check_migrate_payment_term(self, config, payment_terms):
        terms = self.env["account.payment.term"].browse(payment_terms)
        pt_30_percent_now_balance_7_days = terms[0]
        pt_50_percent_3_days_after_end_month_balance_2_months = terms[1]
        pt_2_lines_2_epd = terms[2]
        pt_balance_7_days = terms[3]
        pt_balance_0_days_0_months_eom_false = terms[4]
        pt_balance_0_days_0_months_eom_true = terms[5]
        pt_balance_0_days_1_months_eom_false = terms[6]
        pt_balance_0_days_1_months_eom_true = terms[7]
        pt_balance_15_days_2_months_eom_false = terms[8]
        pt_balance_15_days_2_months_eom_true = terms[9]
        pt_balance_15_days_2_months_eom_true_10_days_after = terms[10]
        pt_balance_5_days_3_months_eom_true_6_days_after = terms[11]

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
                {"value": "percent", "value_amount": 50, "delay_type": "days_after_end_of_next_month", "nb_days": 3},
                {"value": "percent", "value_amount": 50, "delay_type": "days_after", "nb_days": 60},
            ),
        )
        self.assertTrue(pt_2_lines_2_epd.early_discount)
        self.assertEqual(pt_2_lines_2_epd.discount_percentage, 5.0)
        self.assertEqual(pt_2_lines_2_epd.discount_days, 10)
        self.assertEqual(pt_2_lines_2_epd.early_pay_discount_computation, "mixed")
        self.assertRecordValues(
            pt_balance_7_days.line_ids,
            [{"value": "percent", "value_amount": 100, "delay_type": "days_after", "nb_days": 7}],
        )
        self.assertRecordValues(
            pt_balance_0_days_0_months_eom_false.line_ids,
            [{"delay_type": "days_after", "nb_days": 0}],
        )
        self.assertRecordValues(
            pt_balance_0_days_0_months_eom_true.line_ids,
            [{"delay_type": "days_after_end_of_month", "nb_days": 0}],
        )
        self.assertRecordValues(
            pt_balance_0_days_1_months_eom_false.line_ids,
            [{"delay_type": "days_after", "nb_days": 30}],
        )
        self.assertRecordValues(
            pt_balance_0_days_1_months_eom_true.line_ids,
            [{"delay_type": "days_after_end_of_next_month", "nb_days": 0}],
        )
        self.assertRecordValues(
            pt_balance_15_days_2_months_eom_false.line_ids,
            [{"delay_type": "days_after", "nb_days": 75}],
        )
        self.assertRecordValues(
            pt_balance_15_days_2_months_eom_true.line_ids,
            [{"delay_type": "days_after_end_of_next_month", "nb_days": 15}],
        )
        self.assertRecordValues(
            pt_balance_15_days_2_months_eom_true_10_days_after.line_ids,
            [{"delay_type": "days_after_end_of_next_month", "nb_days": 10}],
        )
        self.assertRecordValues(
            pt_balance_5_days_3_months_eom_true_6_days_after.line_ids,
            [{"delay_type": "days_after_end_of_next_month", "nb_days": 6}],
        )

    def prepare(self):
        res = super().prepare()
        res["tests"].append(("_check_migrate_payment_term", self._prepare_test_migrate_prepare_payment_term()))
        return res
