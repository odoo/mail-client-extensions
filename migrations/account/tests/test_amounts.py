from collections import namedtuple

from odoo import fields
from odoo.tests import tagged
from odoo.tools.float_utils import float_compare

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
        for data_iter, new_data_iter in zip(data.value, new_data.value):
            self.assertEqual(data_iter[:2], list(new_data_iter[:2]), self.message)
            self.assertEqual(
                float_compare(
                    float(data_iter[2]),
                    new_data_iter[2],
                    precision_digits=new_data_iter[3] or data_iter[3] or 2,
                ),
                0,
                self.message,
            )

    def invariant(self, date=None):
        cr = self.env.cr
        # In CI, new demo and test data can be added. We should ignore them.
        filter_ = "true"
        if util.on_CI():
            date = date or fields.Datetime.now()
            filter_ = cr.mogrify("l.create_date <= %s", [date]).decode()

        query = util.format_query(
            cr,
            """
            SELECT l.company_id cid,
                   l.account_id aid,
                   sum(round(l.balance, c.decimal_places)),
                   c.decimal_places as dec
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
                      aid,
                      dec
            HAVING sum(round(l.balance, c.decimal_places)) <> 0
             ORDER BY cid,
                      aid
            """,
            filter_=util.SQLStr(filter_),
        )
        cr.execute(query)
        value = cr.fetchall()

        return self.Data(value, str(date))
