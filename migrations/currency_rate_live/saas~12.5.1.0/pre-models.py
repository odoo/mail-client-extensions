# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "res.company", "last_currency_sync_date")
    util.remove_field(cr, "res.config.settings", "last_currency_sync_date")
