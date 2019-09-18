# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_record(cr, "account.ir_cron_reverse_entry")
    util.remove_record(cr, "account.ir_cron_reverse_entry_ir_actions_server")
