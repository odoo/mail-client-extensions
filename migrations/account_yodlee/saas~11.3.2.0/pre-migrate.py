# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "account.online.provider", "yodlee_additional_status")
    util.remove_field(cr, "account.online.provider", "yodlee_last_attempted_refresh")
    util.remove_field(cr, "account.online.provider", "yodlee_next_schedule_refresh")
