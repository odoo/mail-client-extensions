# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("ALTER TABLE account_online_provider ALTER COLUMN status_code TYPE varchar")
    cr.execute("DELETE FROM account_online_wizard")
    for f in "journal_id account_online_id number_added count_account_online_journal".split():
        util.remove_field(cr, "account.online.wizard", f)
