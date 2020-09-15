# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import random
import logging

from datetime import datetime

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase, change_version
from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger(__name__)


def _journal_domain(i):
    # This doesn't migrate. At all.
    # if i%3==0:
    #     return [('type', 'not in', ('bank', 'cash'))]
    return [("type", "in", ("bank", "cash"))]


def _next_company(self, last_id):
    company_ids = self.env["res.company"].search(["!", ("id", "=", last_id)])
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
    def prepare(self):
        with util.no_fiscal_lock(self.env.cr):
            generate_size = 100
            invoice_per_partner = 10
            abs_numbers = 30

            apm_ids = self.env["account.payment.method"].search([]).ids
            aj_ids = self.env["account.journal"].search([("type", "in", ["bank", "cash"])]).ids
            non_aj_ids = self.env["account.journal"].search(["!", ("type", "in", ["bank", "cash"])], limit=5)

            deprecated_accounts = self.env["account.account"].search([("deprecated", "=", True)])
            deprecated_accounts.write({"deprecated": False})

            _logger.info("Generate partners")
            partner_ids = self.env["res.partner"].create(
                [{"name": "Partner %i for payments migration" % i} for i in range(0, generate_size)]
            )
            move_ids = []
            payment_ids = []
            _logger.info("Generate invoices")
            type_field = "move_type" if util.version_gte("saas~13.3") else "type"
            for partner_id in partner_ids:
                for _ in range(0, invoice_per_partner):
                    move_ids.append(
                        self.env["account.move"]
                        .create(
                            {
                                "partner_id": partner_id.id,
                                type_field: "out_invoice",
                                "invoice_line_ids": [(0, 0, {"name": "line", "price_unit": 100, "quantity": 5})],
                            }
                        )
                        .id
                    )

            _logger.info("Validate 80%% of invoices")
            self.env["account.move"].browse([m for m in move_ids if not m % 5 == 0]).post()

            _logger.info("Generate payments")
            for partner_id in partner_ids:
                payment_ids.append(
                    self.env["account.payment"]
                    .create(
                        {
                            "partner_id": partner_id.id,
                            "payment_type": "inbound",
                            "partner_type": "customer",
                            "payment_method_id": random.choice(apm_ids),
                            "journal_id": random.choice(aj_ids),
                            "amount": 1000 if partner_id.id % 3 == 0 else 750 if partner_id.id % 3 == 1 else 300,
                        }
                    )
                    .id
                )

            _logger.info("post 2 payments over 3")
            for payment_id in payment_ids:
                if not payment_id % 3 == 0:
                    self.env["account.payment"].browse(payment_id).post()

            _logger.info("Generate account.bank.statement without move on deprecated accounts")
            abs_ids = self.env["account.bank.statement"].create(
                [
                    {
                        "date": datetime.now().isoformat(),
                        "journal_id": random.choice(
                            self.env["account.journal"].search(_journal_domain(i), limit=1000)
                        ).id,
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
                    for i in range(0, abs_numbers)
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

            for _validate_payments in (True, False):
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
                                payment_ids.append(payment_new.id)

            _logger.info("create some account.bank.statement")
            mig_test = 0
            mig_test_dt = datetime.now().strftime("%Y/%m")
            for _validate_payments in (True, False):
                for journal in aj_ids:
                    for curr in (currency_usd, currency_eur, currency_aud, False):
                        for amnt in (-10, 0, 33):
                            mig_test += 1
                            mig_test_str = f"00000{mig_test}"[-5:]
                            for name in (
                                f"BNK_mig_{mig_test}",
                                "",
                                False,
                                f"BNK/{mig_test_dt}/{mig_test_str}",
                                f"BNK/{mig_test_dt}/00001",
                            ):
                                for lname in ("_", ""):
                                    self.env["account.bank.statement"].create(
                                        {
                                            "name": name,
                                            "date": datetime.now().isoformat(),
                                            "line_ids": [
                                                (
                                                    0,
                                                    0,
                                                    {
                                                        "name": lname,
                                                        "amount": amnt,
                                                        "currency_id": curr.id
                                                        if curr and curr.id != journal.currency_id.id
                                                        else False,
                                                    },
                                                )
                                            ],
                                            "journal_id": journal.id,
                                            "currency_id": curr.id
                                            if curr and curr.id != journal.currency_id.id
                                            else False,
                                        }
                                    )

            # This test doesn't migrate at all
            # _logger.info("create some payments on crappy journal")
            # for journal in non_aj_ids:
            #     for curr in (currency_usd, currency_eur, False):
            #         for amnt in (-10, 33):
            #             mig_test += 1
            #             mig_test_str = f'00000{mig_test}'[-5:]
            #             for name in (
            #                f"BNK_mig_{mig_test}",
            #                "",
            #                False,
            #                f"BNK/{mig_test_dt}/{mig_test_str}",
            #                f"BNK/{mig_test_dt}/00001",
            #             ):
            #                 for lname in ('_', ''):
            #                     self.env['account.bank.statement'].create({
            #                         'name': name,
            #                         'date': datetime.now().isoformat(),
            #                         'line_ids': [(0, 0, {
            #                             'name': lname,
            #                             'amount': amnt,
            #                             # 'currency_id': curr.id if curr and curr.id!=journal.currency_id.id else False,
            #                         })],
            #                         'journal_id': journal.id,
            #                         'currency_id': curr.id if curr and curr.id!=journal.currency_id.id else False,
            #                     })

            for _ in non_aj_ids:
                pass  # dummy loop to keep variable used

            _logger.info("create some account.bank.statement on various account and various currencies")
            cr = self.env.cr
            cr.execute("select account_id,count(*) as nbr from account_move_line group by 1 having count(*)>1")
            for acc in cr.fetchall():
                account_id = acc[0]
                for journal in aj_ids:
                    for curr in (currency_usd, currency_eur, currency_aud, False):
                        mig_test += 1
                        mig_test_str = f"00000{mig_test}"[-5:]
                        for name in (
                            f"BNK_mig_{mig_test}",
                            "",
                            False,
                            f"BNK/{mig_test_dt}/{mig_test_str}",
                            f"BNK/{mig_test_dt}/00001",
                        ):
                            for lname in ("_", ""):
                                self.env["account.bank.statement"].create(
                                    {
                                        "name": name,
                                        "date": datetime.now().isoformat(),
                                        "line_ids": [
                                            (
                                                0,
                                                0,
                                                {
                                                    "name": lname,
                                                    "amount": amnt,
                                                    "currency_id": curr.id
                                                    if curr and curr.id != journal.currency_id.id
                                                    else False,
                                                    "account_id": account_id,
                                                },
                                            )
                                        ],
                                        "journal_id": journal.id,
                                        "currency_id": curr.id if curr and curr.id != journal.currency_id.id else False,
                                    }
                                )

            _logger.info("Some account.payment from res.partner.bank on wrong company")
            last_company_id = -1
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
                                    "amount": amnt,
                                    "currency_id": curr.id if curr and curr.id != journal.currency_id.id else False,
                                    "bank_account_id": rpb_id.id,
                                },
                            )
                        ],
                        "journal_id": random.choice(aj_ids.ids),
                        "currency_id": curr.id if curr and curr.id != journal.currency_id.id else False,
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
            abs_ids[0].line_ids[0].write({"account_id": False})
            abs_ids[1].line_ids[0].account_id.write({"deprecated": True})

            # Deprecate an account
            for payment in self.env["account.payment"].search(
                [("id", "in", payment_ids), ("state", "=", "draft")], limit=3
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
                "move_ids": move_ids,
                "partner_ids": partner_ids.ids,
                "payment_ids": payment_ids,
            }

    def check(self, init):
        return True
