# -*- coding: utf-8 -*-
from odoo import fields

from .common import TestAccountingSetupCommon
from odoo.addons.base.maintenance.migrations.testing import change_version


@change_version("16.0")
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

    def _prepare_test_statement_lines_null_sequence(self):
        """Test the migration of a statement having some lines with a NULL sequence."""
        statement = self.env["account.bank.statement"].create(
            {
                "journal_id": self.bank_journal.id,
                "date": "2021-01-01",
                "line_ids": [
                    fields.Command.create(
                        {"payment_ref": str(index), "amount": 100.0, "date": "2020-01-01", "sequence": sequence}
                    )
                    for index, sequence in enumerate(range(-2, 3))
                ],
            }
        )

        self.env.cr.execute(
            """
                UPDATE account_bank_statement_line
                SET sequence = NULL
                WHERE sequence IN (-1, 1)
                AND statement_id = %s
            """,
            [statement.id],
        )

        return statement.ids

    def _check_test_statement_lines_null_sequence(self, config, statement_id):
        statement = self.env["account.bank.statement"].browse(statement_id)
        for line in statement.line_ids:
            self.assertTrue(line.internal_index)

        self.assertRecordValues(
            statement.line_ids.sorted(),
            [
                {"payment_ref": "3"},
                {"payment_ref": "1"},
                {"payment_ref": "0"},
                {"payment_ref": "2"},
                {"payment_ref": "4"},
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
        res["tests"].append(
            ("_check_test_statement_lines_null_sequence", self._prepare_test_statement_lines_null_sequence())
        )
        return res
