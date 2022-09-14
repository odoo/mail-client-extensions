# -*- coding: utf-8 -*-
from odoo import fields

from .common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("saas~15.5")
class TestOptionalBankStatements(TestAccountingSetupCommon):

    # -------------------------------------------------------------------------
    # TESTS
    # -------------------------------------------------------------------------

    def _prepare_test_statements(self):
        valid_statement = self.env["account.bank.statement"].create(
            {
                "balance_start": 0,
                "balance_end_real": 300.0,
                "journal_id": self.bank_journal.id,
                "date": "2020-01-02",
                "line_ids": [
                    fields.Command.create({"payment_ref": "line1", "amount": 200.0, "date": "2020-01-02"}),
                    fields.Command.create({"payment_ref": "line2", "amount": 100.0, "date": "2020-01-01"}),
                ],
            }
        )
        # Balances are correct but some transactions are missing inside.
        incomplete_statement = self.env["account.bank.statement"].create(
            {
                "balance_start": 300,
                "balance_end_real": 1500.0,
                "journal_id": self.bank_journal.id,
                "date": "2020-01-10",
                "line_ids": [
                    fields.Command.create({"payment_ref": "line4", "amount": 400.0, "date": "2020-01-04"}),
                    fields.Command.create({"payment_ref": "line3", "amount": 300.0, "date": "2020-01-03"}),
                ],
            }
        )
        valid_statement_not_posted = self.env["account.bank.statement"].create(
            {
                "balance_start": 1500.0,
                "balance_end_real": 2800.0,
                "journal_id": self.bank_journal.id,
                "date": "2020-01-12",
                "line_ids": [
                    fields.Command.create({"payment_ref": "line7", "amount": 700.0, "date": "2020-01-12"}),
                    fields.Command.create({"payment_ref": "line6", "amount": 600.0, "date": "2020-01-11"}),
                ],
            }
        )
        # Statement is correct but a statement is missing before.
        invalid_statement = self.env["account.bank.statement"].create(
            {
                "balance_start": 3600,
                "balance_end_real": 5500.0,
                "journal_id": self.bank_journal.id,
                "date": "2020-01-17",
                "line_ids": [
                    fields.Command.create(
                        {"payment_ref": "line9", "amount": 900.0, "date": "2020-01-15", "sequence": 5}
                    ),
                    fields.Command.create(
                        {"payment_ref": "line10", "amount": 1000.0, "date": "2020-01-16", "sequence": 3}
                    ),
                ],
            }
        )
        (valid_statement + incomplete_statement + invalid_statement).button_post()
        return [(valid_statement + incomplete_statement + valid_statement_not_posted + invalid_statement).ids]

    def _check_test_statements(self, config, statement_ids):
        statements = self.env["account.bank.statement"].browse(statement_ids)

        # Ensure the transactions are well-ordered.
        lines = statements.line_ids.sorted()
        self.assertRecordValues(
            lines,
            [
                {"payment_ref": "line10"},
                {"payment_ref": "line9"},
                {"payment_ref": "line7"},
                {"payment_ref": "line6"},
                {"payment_ref": "line4"},
                {"payment_ref": "line3"},
                {"payment_ref": "line1"},
                {"payment_ref": "line2"},
            ],
        )

        # Check the statements.
        self.assertRecordValues(
            statements,
            [
                {
                    "date": fields.Date.from_string("2020-01-02"),
                    "is_complete": True,
                    "first_line_index": statements[0].line_ids.sorted()[-1].internal_index,
                },
                {
                    "date": fields.Date.from_string("2020-01-04"),
                    "is_complete": False,
                    "first_line_index": statements[1].line_ids.sorted()[-1].internal_index,
                },
                {
                    "date": fields.Date.from_string("2020-01-12"),
                    "is_complete": True,
                    "first_line_index": statements[2].line_ids.sorted()[-1].internal_index,
                },
                {
                    "date": fields.Date.from_string("2020-01-16"),
                    "is_complete": True,
                    "first_line_index": statements[3].line_ids.sorted()[-1].internal_index,
                },
            ],
        )

    # -------------------------------------------------------------------------
    # SETUP
    # -------------------------------------------------------------------------

    def prepare(self):
        res = super().prepare()
        self.bank_journal = self.env["account.journal"].search(
            [
                ("company_id", "=", self.env.company.id),
                ("type", "=", "bank"),
            ]
        )
        res["config"]["bank_journal_id"] = self.bank_journal.id
        res["tests"].append(("_check_test_statements", self._prepare_test_statements()))
        return res
