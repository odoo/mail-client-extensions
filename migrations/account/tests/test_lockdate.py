from datetime import datetime, timedelta

from odoo.addons.base.maintenance.migrations import util
from odoo.addons.base.maintenance.migrations.testing import UpgradeCase


class LockDateCase(UpgradeCase):
    """
    Set lock_date to ensure it's handled by migration
    """

    def prepare(self):
        lock_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        columns = [col for col in util.get_columns(self.env.cr, "res_company") if col.endswith("_lock_date")]
        if not columns:
            return
        query = "UPDATE res_company SET {} WHERE name NOT IN ('TestLockDatesRework 17.5 upgrade company', 'company for TestPaymentPocalypse')".format(
            ",".join("{} = %(lock_date)s".format(col) for col in columns),
        )
        self.env.cr.execute(query, locals())

    def check(self, init):
        return True
