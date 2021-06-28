# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version


@change_version("saas~14.4")
class TestJournalMethods(UpgradeCase):
    def _prepare_test_migrate_common_payment_methods(self):
        """
        First test: make sure that payment methods lines are properly added to the journal containing the payment methods
        before the migration.
        """
        inbound_payment_method = self.env["account.payment.method"].create(
            {"name": "Inbound method 1", "code": "im1", "payment_type": "inbound"}
        )
        outbound_payment_method = self.env["account.payment.method"].create(
            {"name": "Outbound method 1", "code": "om1", "payment_type": "outbound"}
        )
        journal = self.env["account.journal"].create(
            {
                "name": "Test journal 1",
                "code": "tj1",
                "type": "bank",
            }
        )

        journal.inbound_payment_method_ids = inbound_payment_method
        journal.outbound_payment_method_ids = outbound_payment_method

        return {"journal_id": journal.id, "ipm_id": inbound_payment_method.id, "opm_id": outbound_payment_method.id}

    def _prepare_test_migrate_journal_accounts(self):
        """
        Second test: make sure that the account that was set on the journal before migration is properly set on the payment method
        line if it is different from the one on the company
        """
        debit_account = self.env["account.account"].create(
            {
                "name": "Test debit account",
                "code": "978645",
                "user_type_id": self.env.ref("account.data_account_type_expenses").id,
            }
        )
        inbound_payment_method = self.env["account.payment.method"].create(
            {
                "name": "Inbound method 2",
                "code": "im2",
                "payment_type": "inbound",
            }
        )
        outbound_payment_method = self.env["account.payment.method"].create(
            {"name": "Outbound method 2", "code": "om2", "payment_type": "outbound"}
        )
        journal = self.env["account.journal"].create(
            {
                "name": "Test journal 2",
                "code": "tj2",
                "type": "bank",
                "payment_debit_account_id": debit_account.id,
            }
        )

        journal.inbound_payment_method_ids = inbound_payment_method
        journal.outbound_payment_method_ids = outbound_payment_method

        return {
            "journal_id": journal.id,
            "ipm_id": inbound_payment_method.id,
            "opm_id": outbound_payment_method.id,
            "debit_account_id": debit_account.id,
        }

    def _prepare_test_migrate_payment_acquirer(self, acquirer_journal):
        """
        Third test: make sure that an acquirer linked to a journal before migration has a method line linking it to it after.
        """
        if not util.module_installed(self.env.cr, "payment"):
            return {}

        acquirer = self.env["payment.acquirer"].create(
            {
                "name": "Test acquirer",
                "company_id": acquirer_journal.company_id.id,
                "state": "disabled",
                "journal_id": acquirer_journal.id,
                "provider": "none" if util.version_gte("saas~14.3") else "manual",
            }
        )

        return {"journal_id": acquirer_journal.id, "acquirer_id": acquirer.id}

    def _prepare_test_migrate_account_payment(self):
        """
        During the migration, payments change from storing the payment method to the payment method line.
        Test this too to ensure that it is working as expected.
        """
        inbound_payment_method = self.env["account.payment.method"].create(
            {"name": "Inbound method 4", "code": "im4", "payment_type": "inbound"}
        )
        journal = self.env["account.journal"].create(
            {
                "name": "Test journal 4",
                "code": "tj4",
                "type": "bank",
            }
        )
        journal.inbound_payment_method_ids = inbound_payment_method

        payment = self.env["account.payment"].create(
            {
                "amount": 100.0,
                "payment_type": "inbound",
                "partner_type": "customer",
                "journal_id": journal.id,
                "payment_method_id": inbound_payment_method.id,
            }
        )

        return {"journal_id": journal.id, "payment_id": payment.id, "payment_method_id": inbound_payment_method.id}

    def _prepare_test_migrate_account_payment_acquirer(self, acquirer_journal):
        """
        Payment linked to an "acquirer" before the migration are actually linked to the acquirer journal
        and the electronic payment method.
        This payment method is deleted during the migration, so we need to make sure that after migration,
        the payment is linked to the newly created line for this acquirer.
        """
        if not util.module_installed(self.env.cr, "payment"):
            return {}

        electronic = self.env.ref("payment.account_payment_method_electronic_in")

        acquirer_journal.inbound_payment_method_ids = [(4, electronic.id)]

        payment = self.env["account.payment"].create(
            {
                "amount": 100.0,
                "payment_type": "inbound",
                "partner_type": "customer",
                "journal_id": acquirer_journal.id,
                "payment_method_id": electronic.id,
            }
        )

        return {"journal_id": acquirer_journal.id, "payment_id": payment.id}

    def _prepare_test_migrate_account_payment_electronic(self):
        """
        Payment linked to the electronic payment method of a regular journal, not one linked to an acquirer,
        can be linked the the manual payment method line of the journal
        """
        if not util.module_installed(self.env.cr, "payment"):
            return {}

        journal = self.env["account.journal"].create({"name": "Test journal 6", "code": "tj6", "type": "bank"})
        electronic = self.env.ref("payment.account_payment_method_electronic_in")

        journal.inbound_payment_method_ids = [(4, electronic.id)]

        payment = self.env["account.payment"].create(
            {
                "amount": 100.0,
                "payment_type": "inbound",
                "partner_type": "customer",
                "journal_id": journal.id,
                "payment_method_id": electronic.id,
            }
        )

        return {"journal_id": journal.id, "payment_id": payment.id}

    def _check_test_migrate_common_payment_methods(self, values):
        journal = self.env["account.journal"].browse(values["journal_id"])
        inbound_payment_method_code = self.env["account.payment.method"].browse(values["ipm_id"]).code
        outbound_payment_method_code = self.env["account.payment.method"].browse(values["opm_id"]).code

        ipm_in_journal = inbound_payment_method_code in journal.inbound_payment_method_line_ids.mapped("code")
        opm_in_journal = outbound_payment_method_code in journal.outbound_payment_method_line_ids.mapped("code")

        self.assertTrue(ipm_in_journal and opm_in_journal)

    def _check_test_migrate_journal_accounts(self, values):
        journal = self.env["account.journal"].browse(values["journal_id"])
        inbound_payment_method_code = self.env["account.payment.method"].browse(values["ipm_id"]).code
        outbound_payment_method_code = self.env["account.payment.method"].browse(values["opm_id"]).code

        ipm_line = journal.inbound_payment_method_line_ids.filtered(lambda l: l.code == inbound_payment_method_code)
        opm_line = journal.outbound_payment_method_line_ids.filtered(lambda l: l.code == outbound_payment_method_code)

        self.assertEqual(ipm_line.payment_account_id.id, values["debit_account_id"])
        # We didn't specify a credit account on the journal, so it'll not be saved on the payment lines
        self.assertEqual(opm_line.payment_account_id.id, False)

    def _check_test_migrate_payment_acquirer(self, values):
        if not util.module_installed(self.env.cr, "payment"):
            return

        journal = self.env["account.journal"].browse(values["journal_id"])
        acquirer = self.env["payment.acquirer"].browse(values["acquirer_id"])

        self.assertEqual(acquirer.journal_id, journal)

    def _check_test_migrate_account_payment(self, values):
        journal = self.env["account.journal"].browse(values["journal_id"])
        payment = self.env["account.payment"].browse(values["payment_id"])

        journal_line = journal.inbound_payment_method_line_ids.filtered(
            lambda l: l.payment_method_id.id == values["payment_method_id"]
        )

        self.assertEqual(payment.payment_method_line_id, journal_line)

    def _check_test_migrate_account_payment_acquirer(self, values):
        if not util.module_installed(self.env.cr, "payment"):
            return

        journal = self.env["account.journal"].browse(values["journal_id"])
        payment = self.env["account.payment"].browse(values["payment_id"])

        journal_line = journal.inbound_payment_method_line_ids.filtered(lambda l: l.code == "none")

        self.assertEqual(payment.payment_method_line_id, journal_line)

    def _check_test_migrate_account_payment_electronic(self, values):
        if not util.module_installed(self.env.cr, "payment"):
            return

        journal = self.env["account.journal"].browse(values["journal_id"])
        payment = self.env["account.payment"].browse(values["payment_id"])

        journal_line = journal.inbound_payment_method_line_ids.filtered(lambda l: l.code == "manual")

        self.assertEqual(payment.payment_method_line_id, journal_line)

    def prepare(self):
        acquirer_journal = self.env["account.journal"].create({"name": "Test journal 3", "code": "tj3", "type": "bank"})
        self.env["account.payment.method"].create(
            {"name": "Acquirer method", "code": "none", "payment_type": "inbound"}
        )

        return {
            "14.4-test-journal-methods": [
                self._prepare_test_migrate_common_payment_methods(),
                self._prepare_test_migrate_journal_accounts(),
                self._prepare_test_migrate_payment_acquirer(acquirer_journal),
                self._prepare_test_migrate_account_payment(),
                self._prepare_test_migrate_account_payment_acquirer(acquirer_journal),
                self._prepare_test_migrate_account_payment_electronic(),
            ]
        }

    def check(self, init):
        self._check_test_migrate_common_payment_methods(init["14.4-test-journal-methods"][0])
        self._check_test_migrate_journal_accounts(init["14.4-test-journal-methods"][1])
        self._check_test_migrate_payment_acquirer(init["14.4-test-journal-methods"][2])
        self._check_test_migrate_account_payment(init["14.4-test-journal-methods"][3])
        self._check_test_migrate_account_payment_acquirer(init["14.4-test-journal-methods"][4])
        self._check_test_migrate_account_payment_electronic(init["14.4-test-journal-methods"][5])
