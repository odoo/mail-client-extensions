# -*- coding: utf-8 -*-

from collections import namedtuple

from odoo import fields
from odoo.tests import tagged

from odoo.addons.base.maintenance.migrations import util
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
    # save date to ignore new moves created by demo and tests data
    Data = namedtuple("Data", "value date")

    def prepare(self):
        if not util.version_gte("saas~13.4"):
            return None
        return super().prepare()

    def check(self, value):
        if not value:
            return
        data = self.Data(*value)

        new_data = self.invariant(date=data.date)
        self.assertEqual(
            data.value,
            self.convert_check(new_data.value),
            self.message,
        )

    def invariant(self, date=None):
        # In CI, new demo and test data can be added. We should ignore them.
        filter_ = "true"
        if util.on_CI():
            date = date or fields.Datetime.now()
            filter_ = self.env.cr.mogrify("l.create_date <= %s", [date]).decode()

        query = f"""
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
             WHERE {filter_}
             GROUP BY cid,
                      aid
            HAVING sum(round(l.balance, c.decimal_places)) <> 0
             ORDER BY cid,
                      aid;
        """
        self.env.cr.execute(query)
        value = self.env.cr.fetchall()

        return self.Data(value, str(date))
