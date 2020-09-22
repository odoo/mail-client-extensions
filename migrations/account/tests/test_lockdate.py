# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
from datetime import datetime, timedelta

from odoo.addons.base.maintenance.migrations.testing import UpgradeCase
from odoo.addons.base.maintenance.migrations import util


class LockDateCase(UpgradeCase):
    """
        Set lock_date to ensure it's handled by migration
    """

    def prepare(self):
        lock_date = (datetime.now() + timedelta(days=15)).strftime("%Y-%m-%d")
        columns = [col for col in util.get_columns(self.env.cr, "res_company")[0] if col.endswith("_lock_date")]
        if not columns:
            return
        query = "UPDATE res_company SET {}".format(",".join("{} = %(lock_date)s".format(col) for col in columns))
        self.env.cr.execute(query, locals())

    def check(self, init):
        return True
