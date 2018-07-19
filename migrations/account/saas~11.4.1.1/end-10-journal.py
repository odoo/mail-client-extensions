# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    Journal = util.env(cr)["account.journal"]
    cr.execute("SELECT id, COALESCE(write_uid, create_uid, 1) FROM account_journal WHERE type='purchase'")
    for jid, uid in cr.fetchall():
        Journal.browse(jid).sudo(user=uid)._update_mail_alias({})
