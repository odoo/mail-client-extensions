# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from collections import namedtuple

from odoo import release
from odoo.tests import tagged
from odoo.tools.parse_version import parse_version

from odoo.addons.base.maintenance.migrations.testing import IntegrityCase


@tagged("account_balance")
class TestAccountAmountsUnchanged(IntegrityCase):
    """
    This test will check that the balance, as given by the sum of move lines,
    is invariant over the upgrade.

    Debit/Credit may change over an upgrade but the balance must remain the same.

    During the payment refactoring of saas~13.4.1.1 some moves may change state,
    draft->posted, therefore we perform the integrity check only if upgrading
    from 14.0 onwards.
    """

    # data returned from the invariant
    # save company ids to avoid conflict with test_total_amount_signed.py
    Data = namedtuple("Data", "value version company_ids")

    def check(self, value):
        data = self.Data(*value)
        source_version = parse_version(data.version)

        # Due to a conflicting UpgradeCase in runbot, we need to skip the current test
        # from 14.0 to saas~14.3 when we detect data for TestTagNoInvert on the DB.
        self.env.cr.execute(
            "SELECT COUNT(*) FROM upgrade_test_data WHERE key = %s",
            ["account_reports.tests.test_14_1_tag_no_invert.TestTagNoInvert"],
        )
        if source_version >= parse_version("saas~14.3") or (
            source_version >= parse_version("14.0") and self.env.cr.fetchone()[0] == 0
        ):
            new_data = self.invariant(company_ids=data.company_ids)
            self.assertEqual(
                data.value,
                self.convert_check(new_data.value),
                self.message,
            )

    def invariant(self, company_ids=None):
        if company_ids is None:
            self.env.cr.execute("""
                SELECT id
                  FROM res_company;
            """)
            company_ids = list(r[0] for r in self.env.cr.fetchall())

        query = """
            SELECT l.company_id cid,
                   l.account_id aid,
                   sum(round(l.balance, c.decimal_places))
              FROM account_move_line l
              JOIN account_move m
                ON l.move_id = m.id
               AND m.state = 'posted'
              JOIN account_account a
                ON l.account_id = a.id
              JOIN res_company co
                ON l.company_id = co.id
              JOIN res_currency c
                ON co.currency_id = c.id
             WHERE l.company_id = any(%s)
             GROUP BY cid,
                      aid
            HAVING sum(round(l.balance, c.decimal_places)) <> 0
             ORDER BY cid,
                      aid;
        """
        self.env.cr.execute(query, [company_ids])
        value = self.env.cr.fetchall()

        return self.Data(value, release.series, company_ids)
