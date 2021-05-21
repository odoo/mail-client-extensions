# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import itertools
import logging
import random
from datetime import datetime

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version

_logger = logging.getLogger(__name__)


def _journal_domain(i):
    # This doesn't migrate. At all.
    # if i%3==0:
    #     return [('type', 'not in', ('bank', 'cash'))]
    return [("type", "in", ("bank", "cash"))]


def _next_company(self, last_id):
    company_ids = self.env["res.company"].search(["!", ("id", "=", last_id)])
    if not company_ids:
        return last_id
    return random.choice(company_ids.ids)


def _new_account(self, acc, currency_id):
    type_id = self.env.ref("account.data_account_type_liquidity").id

    return (
        self.env["account.account"]
        .create(
            {
                "name": f"10000{acc}",
                "code": f"MIG_{acc}",
                "user_type_id": type_id,
                "currency_id": currency_id,
            }
        )
        .id
    )


@change_version("13.4")
class CheckPayments(UpgradeCase):

    # TODO move this to base class
    def patch(self, obj, key, val):
        """Do the patch ``setattr(obj, key, val)``, and prepare cleanup."""
        old = getattr(obj, key)
        setattr(obj, key, val)
        self.addCleanup(setattr, obj, key, old)

    def prepare(self):
        PARTNER_COUNT = 100
        INVOICE_PER_PARTNER = 10
        BANK_STATEMENT_COUNT = 30
        SAMPLE_BANK_STATEMENTS = 512

        if not self.env["account.journal"].search_count(
            [("type", "=", "sale"), ("company_id", "=", self.env.company.id)]
        ):
            self.skipTest("No sale journal found. Is a CoA installed?")

        if hasattr(self.env["account.move"], "_l10n_co_edi_is_l10n_co_edi_required"):
            # Do not upload test invoices
            self.patch(type(self.env["account.move"]), "_l10n_co_edi_is_l10n_co_edi_required", lambda s: False)

        with util.no_fiscal_lock(self.env.cr):

            sepa = self.env["ir.model.data"].xmlid_to_res_id("account_sepa.account_payment_method_sepa_ct")
            aba = self.env["ir.model.data"].xmlid_to_res_id("l10n_au_aba.account_payment_method_aba_ct")
            apm_ids = (
                self.env["account.payment.method"].search([("id", "not in", [sepa, aba]), ("code", "!=", "sdd")]).ids
            )
            aj_ids = self.env["account.journal"].search([("type", "in", ["bank", "cash"])]).ids

            if util.module_installed(self.env.cr, "l10n_latam_invoice_document"):
                latam_journals = self.env["account.journal"].search([("l10n_latam_use_documents", "=", True)])
                latam_journals.write({"l10n_latam_use_documents": False})

            deprecated_accounts = self.env["account.account"].search([("deprecated", "=", True)])
            deprecated_accounts.write({"deprecated": False})

            _logger.info("Generate partners")
            belgium = self.env["ir.model.data"].xmlid_to_res_id("base.be")
            partner_ids = self.env["res.partner"].create(
                [
                    {
                        "name": f"Partner {i} for payments upgrade",
                        "street": f"Main Street {i}",
                        "zip": f"{i:04}",
                        "city": "City",
                        "country_id": belgium,
                    }
                    for i in range(PARTNER_COUNT)
                ]
            )

            _logger.info("Generate invoices")
            type_field = "move_type" if util.version_gte("saas~13.3") else "type"

            if util.module_installed(self.env.cr, "l10n_it_edi"):
                # l10n_it_edi require to have exactly one tax set on the invoice line
                # see https://github.com/odoo/odoo/blob/13.0/addons/l10n_it_edi/models/account_invoice.py#L131-L133
                domain = [("type_tax_use", "=", "sale"), ("amount_type", "=", "percent"), ("amount", "=", 0)]
                tax0 = self.env["account.tax"].search(domain, limit=1).ids
            else:
                tax0 = []
            moves = self.env["account.move"].create(
                [
                    {
                        "partner_id": partner.id,
                        type_field: "out_invoice",
                        "invoice_line_ids": [
                            (0, 0, {"name": "line", "price_unit": 100, "quantity": 5, "tax_ids": [(6, 0, tax0)]})
                        ],
                    }
                    for partner in partner_ids
                    for _ in range(INVOICE_PER_PARTNER)
                ]
            )

            _logger.info("Validate 80% of invoices")
            moves.filtered(lambda m: m.id % 5 == 0).post()

            _logger.info("Generate payments")
            payments = self.env["account.payment"].create(
                [
                    {
                        "partner_id": partner.id,
                        "payment_type": "inbound",
                        "partner_type": "customer",
                        "payment_method_id": random.choice(apm_ids),
                        "journal_id": random.choice(aj_ids),
                        "amount": [1000, 750, 300][partner.id % 3],
                    }
                    for partner in partner_ids
                ]
            )

            _logger.info("post 2 payments over 3")
            payments.filtered(lambda p: p.id % 3 == 0).post()

            _logger.info("Generate account.bank.statement without move on deprecated accounts")
            journals = self.env["account.journal"].search(_journal_domain(0), limit=1000)
            bank_statements = self.env["account.bank.statement"].create(
                [
                    {
                        "date": datetime.now().isoformat(),
                        "journal_id": random.choice(journals.ids),
                        "line_ids": [
                            (
                                0,
                                0,
                                {
                                    "name": "line",
                                    "date": datetime.now().isoformat(),
                                    "amount": 42,
                                    "partner_id": random.choice(partner_ids.ids),
                                },
                            )
                        ],
                    }
                    for _ in range(BANK_STATEMENT_COUNT)
                ]
            )

            # Should also deprecate default credit/debit accounts

            # Should have a payment in another currency than the bank account journal one.
            # And a payment without currency
            _logger.info("Payments in various currencies")
            currency_usd = self.env.ref("base.USD")
            currency_eur = self.env.ref("base.EUR")
            currency_aud = self.env.ref("base.AUD")

            aj_ids = self.env["account.journal"].create(
                [
                    {
                        "code": "mig_usd",
                        "currency_id": currency_usd.id,
                        "name": "Migration test in USD",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "001", currency_usd.id),
                        "default_credit_account_id": _new_account(self, "002", currency_usd.id),
                    },
                    {
                        "code": "mig_eur",
                        "currency_id": currency_eur.id,
                        "name": "Migration test in EUR",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "003", currency_eur.id),
                        "default_credit_account_id": _new_account(self, "004", currency_eur.id),
                    },
                    {
                        "code": "mig_aud",
                        "currency_id": currency_aud.id,
                        "name": "Migration test in AUD",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "005", currency_aud.id),
                        "default_credit_account_id": _new_account(self, "006", currency_aud.id),
                    },
                    {
                        "code": "mig_usd_to_eur",
                        "currency_id": currency_usd.id,
                        "name": "Migration test in USD->EUR",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "007", currency_usd.id),
                        "default_credit_account_id": _new_account(self, "008", currency_usd.id),
                    },
                    {
                        "code": "mig_eur_to_usd",
                        "currency_id": currency_eur.id,
                        "name": "Migration test in EUR->USD",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "009", currency_eur.id),
                        "default_credit_account_id": _new_account(self, "010", currency_eur.id),
                    },
                    {
                        "code": "mig_usd_to_aud",
                        "currency_id": currency_usd.id,
                        "name": "Migration test in USD->AUD",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "011", currency_usd.id),
                        "default_credit_account_id": _new_account(self, "012", currency_usd.id),
                    },
                    {
                        "code": "mig_eur_to_aud",
                        "currency_id": currency_eur.id,
                        "name": "Migration test in EUR->AUD",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "013", currency_eur.id),
                        "default_credit_account_id": _new_account(self, "014", currency_eur.id),
                    },
                    {
                        "code": "mig_aud_to_usd",
                        "currency_id": currency_aud.id,
                        "name": "Migration test in AUD->USD",
                        "type": "bank",
                        "default_debit_account_id": _new_account(self, "015", currency_aud.id),
                    },
                    {
                        "code": "mig_aud_to_eur",
                        "currency_id": currency_aud.id,
                        "name": "Migration test in AUD->EUR",
                        "type": "bank",
                        "default_credit_account_id": _new_account(self, "018", currency_aud.id),
                    },
                ]
            )
            shared_1 = _new_account(self, "019", currency_eur.id)
            shared_2 = _new_account(self, "020", currency_eur.id)
            aj_ids |= self.env["account.journal"].create(
                {
                    "code": "mig_shared_1",
                    "currency_id": currency_eur.id,
                    "name": "Shared account 1",
                    "type": "bank",
                    "default_debit_account_id": shared_2,
                    "default_credit_account_id": shared_1,
                }
            )
            aj_ids |= self.env["account.journal"].create(
                {
                    "code": "mig_shared_2",
                    "currency_id": currency_eur.id,
                    "name": "Shared account 2",
                    "type": "bank",
                    "default_debit_account_id": shared_1,
                    "default_credit_account_id": shared_2,
                }
            )

            # for _validate_payments in (True, False):
            if True:
                for curr in (currency_usd, currency_eur, currency_aud):
                    for journal in aj_ids:
                        for apm in apm_ids:
                            for _ in range(3):
                                payment_new = self.env["account.payment"].create(
                                    {
                                        "partner_id": random.choice(partner_ids.ids),
                                        "payment_type": "inbound",
                                        "partner_type": "customer",
                                        "payment_method_id": apm,
                                        "journal_id": journal.id,
                                        "amount": 42,
                                        "currency_id": curr.id,
                                    }
                                )
                                # if validate_payments:
                                #     payment_new.post()
                                payments |= payment_new

            _logger.info("create some account.bank.statement")

            this_month = datetime.now().strftime("%Y/%m")
            self.env["account.move.line"].flush()
            cr = self.env.cr
            cr.execute(
                "SELECT account_id FROM account_move_line WHERE move_id IN %s GROUP BY account_id HAVING count(*) > 1",
                [tuple(moves.ids)],
            )
            accounts = [a for a, in cr.fetchall()] + [False]

            combinations = itertools.product(
                accounts,
                aj_ids,
                (currency_usd, currency_eur, currency_aud, False),
                (-10, 0, 33),  # amount
                ("BNK_mig_{i:05}", "", False, "BNK/{this_month}/{i:05}", "BNK/{this_month}/00001"),
                ("_", ""),
            )
            for i, (account, journal, curr, amnt, name, lname) in enumerate(
                random.sample(list(combinations), SAMPLE_BANK_STATEMENTS)
            ):
                line = {
                    "name": lname,
                    "amount": amnt,
                    "currency_id": curr.id if curr and curr.id != journal.currency_id.id else False,
                }
                if account:
                    line["account_id"] = account
                data = {
                    "name": name.format(i=i, this_month=this_month) if name else False,
                    "date": datetime.now().isoformat(),
                    "line_ids": [(0, 0, line)],
                    "journal_id": journal.id,
                    "currency_id": curr.id if curr and curr.id != journal.currency_id.id else False,
                }
                self.env["account.bank.statement"].create(data)

            _logger.info("Some account.payment from res.partner.bank on wrong company")
            last_company_id = -1
            mig_test = SAMPLE_BANK_STATEMENTS + 1
            mig_test_dt = this_month
            for partner in partner_ids:
                mig_test += 1
                mig_test_str = f"00000{mig_test}"[-5:]
                last_company_id = _next_company(self, last_company_id)
                rpb_id = self.env["res.partner.bank"].create(
                    {"acc_number": "0123-%s" % partner.id, "partner_id": partner.id, "company_id": last_company_id}
                )
                self.env["account.bank.statement"].create(
                    {
                        "name": f"BNK/{mig_test_dt}/{mig_test_str}",
                        "date": datetime.now().isoformat(),
                        "line_ids": [
                            (
                                0,
                                0,
                                {
                                    "name": "_",
                                    "amount": 27,
                                    "currency_id": False,
                                    "bank_account_id": rpb_id.id,
                                },
                            )
                        ],
                        "journal_id": random.choice(aj_ids.ids),
                        "currency_id": False,
                    }
                )

                # self.env['account.payment'].create({
                #     "partner_id": partner.id,
                #     'payment_type': 'inbound',
                #     'partner_type': 'customer',
                #     'payment_method_id': random.choice(apm_ids),
                #     'journal_id': journal.id,
                #     "amount": 42,
                #     'currency_id': currency_eur.id,
                #
                # })

            # Deprecate accounts deprecated before test
            bank_statements[0].line_ids[0].write({"account_id": False})
            bank_statements[1].line_ids[0].account_id.write({"deprecated": True})

            # Deprecate an account
            for payment in self.env["account.payment"].search(
                [("id", "in", payments.ids), ("state", "=", "draft")], limit=3
            ):
                payment.destination_account_id.write({"deprecated": True})
                _logger.info(
                    "deprecated account %s / %s", payment.destination_account_id.id, payment.destination_account_id.name
                )

            deprecated_accounts.write({"deprecated": True})

            for curr_id, jrnl_code in [
                (currency_usd, "mig_eur_to_usd"),
                (currency_eur, "mig_usd_to_eur"),
                (currency_usd, "mig_aud_to_usd"),
                (currency_eur, "mig_aud_to_eur"),
                (currency_aud, "mig_eur_to_aud"),
                (currency_aud, "mig_usd_to_aud"),
            ]:
                self.env.cr.execute("UPDATE account_journal SET currency_id=%s WHERE code=%s", [curr_id.id, jrnl_code])

            # Set same move_name on some bank.statement.line to "simulate" a reconcile...
            self.env.cr.execute(
                """
                WITH absl_ids AS (SELECT id
                                    FROM account_bank_statement_line
                                ORDER BY id desc
                                   LIMIT 10
                )
                UPDATE account_bank_statement_line absl
                   SET move_name='common_name_13/3'
                  FROM absl_ids
                 WHERE absl.id=absl_ids.id
            """
            )
            return {
                "move_ids": moves.ids,
                "partner_ids": partner_ids.ids,
                "payment_ids": payments.ids,
            }

    def check(self, init):
        return True
