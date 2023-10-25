import logging

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

_logger = logging.getLogger(__name__)


@change_version("saas~13.4")
class RefactoringReconciliation(UpgradeCase):
    def setup_new_currency(self, rate2016, rate2017, **kwargs):
        foreign_currency = self.env["res.currency"].create(
            {
                "rounding": 0.01,
                "position": "after",
                **kwargs,
            }
        )
        self.env["res.currency.rate"].create(
            {
                "name": "2016-01-01",
                "rate": rate2016,
                "currency_id": foreign_currency.id,
                "company_id": self.env.company.id,
            }
        )
        self.env["res.currency.rate"].create(
            {
                "name": "2017-01-01",
                "rate": rate2017,
                "currency_id": foreign_currency.id,
                "company_id": self.env.company.id,
            }
        )
        return foreign_currency

    def _prepare_test_case(
        self,
        debit_balance,
        debit_amount_currency,
        debit_currency_id,
        debit_date,
        credit_balance,
        credit_amount_currency,
        credit_currency_id,
        credit_date,
        expected_values,
    ):
        moves = self.env["account.move"].create(
            [
                {
                    "date": debit_date,
                    "journal_id": self.journal.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "debit_line",
                                "debit": debit_balance,
                                "credit": 0.0,
                                "amount_currency": debit_amount_currency,
                                "currency_id": debit_currency_id,
                                "account_id": self.account_receivable.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "debit_line_counterpart",
                                "debit": 0.0,
                                "credit": debit_balance,
                                "amount_currency": 0.0,
                                "currency_id": False,
                                "account_id": self.account_income.id,
                            },
                        ),
                    ],
                },
                {
                    "date": credit_date,
                    "journal_id": self.journal.id,
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "name": "credit_line",
                                "debit": 0.0,
                                "credit": credit_balance,
                                "amount_currency": credit_amount_currency,
                                "currency_id": credit_currency_id,
                                "account_id": self.account_receivable.id,
                            },
                        ),
                        (
                            0,
                            0,
                            {
                                "name": "credit_line_counterpart",
                                "debit": credit_balance,
                                "credit": 0.0,
                                "amount_currency": 0.0,
                                "currency_id": False,
                                "account_id": self.account_income.id,
                            },
                        ),
                    ],
                },
            ]
        )
        moves.action_post()
        amls = moves.line_ids.filtered(lambda aml: aml.account_id == self.account_receivable)
        amls.reconcile()
        partial = amls.matched_debit_ids

        self.assertRecordValues(partial, [expected_values])

        return partial.id

    def prepare(self):
        test_name = "RefactoringReconciliation"

        self.company = self.env["res.company"].create({"name": f"company for {test_name}"})
        # Create user.
        user = (
            self.env["res.users"]
            .with_context(no_reset_password=True)
            .create(
                {
                    "name": f"user {test_name}",
                    "login": test_name,
                    "groups_id": [
                        (6, 0, self.env.user.groups_id.ids),
                        (4, self.env.ref("account.group_account_user").id),
                    ],
                    "company_ids": [(6, 0, self.company.ids)],
                    "company_id": self.company.id,
                }
            )
        )
        user.partner_id.email = f"{test_name}@test.com"

        self.env = self.env(user=user)
        self.cr = self.env.cr

        chart_template = self.env.ref("l10n_generic_coa.configurable_chart_template", raise_if_not_found=False)
        if not chart_template:
            self.skipTest("Accounting Tests skipped because the user's company has no chart of accounts.")

        chart_template.try_loading(company=self.company)
        # Setup accounts.
        self.account_receivable = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id.type", "=", "receivable")], limit=1
        )
        revenue = self.env.ref("account.data_account_type_revenue").id
        self.account_income = self.env["account.account"].search(
            [("company_id", "=", self.company.id), ("user_type_id", "=", revenue)], limit=1
        )
        # Setup journals.
        self.journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.company.id),
                ("type", "=", "general"),
            ],
            limit=1,
        )
        # Setup currencies.
        self.comp_curr = self.env.company.currency_id
        self.currency1 = self.setup_new_currency(
            3.0,
            2.0,
            name="Gold Coin",
            symbol="☺",
            currency_unit_label="Gold",
            currency_subunit_label="Silver",
        )
        self.currency2 = self.setup_new_currency(
            6.0,
            4.0,
            name="Diamond",
            symbol="💎",
            currency_unit_label="Diamond",
            currency_subunit_label="Carbon",
        )

        return {
            "config": {
                "comp_curr_id": self.comp_curr.id,
                "currency1_id": self.currency1.id,
                "currency2_id": self.currency2.id,
            },
            "partial_ids": [
                # Single-currency
                self._prepare_test_case(
                    debit_balance=100.0,
                    debit_amount_currency=10.0,
                    debit_currency_id=False,
                    debit_date="2016-01-01",
                    credit_balance=100.0,
                    credit_amount_currency=-10.0,
                    credit_currency_id=False,
                    credit_date="2016-01-01",
                    expected_values={
                        "amount": 100.0,
                        "amount_currency": 0.0,
                        "currency_id": False,
                    },
                ),
                # Same foreign-currency
                self._prepare_test_case(
                    debit_balance=100.0,
                    debit_amount_currency=300.0,
                    debit_currency_id=self.currency1.id,
                    debit_date="2016-01-01",
                    credit_balance=100.0,
                    credit_amount_currency=-200.0,
                    credit_currency_id=self.currency1.id,
                    credit_date="2017-01-01",
                    expected_values={
                        "amount": 100.0,
                        "amount_currency": 200.0,
                        "currency_id": self.currency1.id,
                    },
                ),
                # Triple currencies
                self._prepare_test_case(
                    debit_balance=100.0,
                    debit_amount_currency=300.0,
                    debit_currency_id=self.currency1.id,
                    debit_date="2016-01-01",
                    credit_balance=100.0,
                    credit_amount_currency=-400.0,
                    credit_currency_id=self.currency2.id,
                    credit_date="2017-01-01",
                    expected_values={
                        "amount": 100.0,
                        "amount_currency": 0.0,
                        "currency_id": False,
                    },
                ),
            ],
        }

    def check(self, results):
        partials = self.env["account.partial.reconcile"].browse(results["partial_ids"])
        config = results["config"]
        self.assertRecordValues(
            partials,
            [
                # Single-currency
                {
                    "amount": 100.0,
                    "debit_amount_currency": 100.0,
                    "debit_currency_id": config["comp_curr_id"],
                    "credit_amount_currency": 100.0,
                    "credit_currency_id": config["comp_curr_id"],
                },
                # Same foreign-currency
                {
                    "amount": 100.0,
                    "debit_amount_currency": 200.0,
                    "debit_currency_id": config["currency1_id"],
                    "credit_amount_currency": 200.0,
                    "credit_currency_id": config["currency1_id"],
                },
                # Triple currencies
                {
                    "amount": 100.0,
                    "debit_amount_currency": 300.0,
                    "debit_currency_id": config["currency1_id"],
                    "credit_amount_currency": 400.0,
                    "credit_currency_id": config["currency2_id"],
                },
            ],
        )
