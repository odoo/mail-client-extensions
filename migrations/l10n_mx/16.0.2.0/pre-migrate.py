# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Don't drop the column to use it in post
    util.remove_field(cr, "account.account.tag", "nature", drop_column=False)
