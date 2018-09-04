# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    Journal = util.env(cr)["account.journal"]
    User = util.env(cr)["res.users"]
    cr.execute("SELECT id, COALESCE(write_uid, create_uid, 1), company_id FROM account_journal WHERE type='purchase'")
    for jid, uid, cid in cr.fetchall():
        u = User.browse(uid)
        old_cid = u.company_id.id
        if cid!=old_cid:
            if cid not in u.company_ids.ids:
                u.write({'company_ids': [(4, cid)]})
            u.company_id = cid
        Journal.browse(jid).sudo(user=uid)._update_mail_alias({})
        if cid!=old_cid:
            u.company_id = old_cid
