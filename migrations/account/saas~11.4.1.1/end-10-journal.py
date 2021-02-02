# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    Journal = util.env(cr)["account.journal"]
    User = util.env(cr)["res.users"]
    cr.execute("SELECT id, COALESCE(write_uid, create_uid, 1), company_id FROM account_journal WHERE type = 'purchase'")
    for jid, uid, cid in cr.fetchall():
        u = User.browse(uid)
        old_cid = u.company_id.id
        cid_changed = False

        if cid != old_cid:
            if u.active and cid in u.company_ids.ids:
                u.company_id = cid
                cid_changed = True
            else:
                uid = 1
        if not Journal.sudo(user=uid).check_access_rights("write", raise_exception=False):
            uid = 1

        Journal.browse(jid).sudo(user=uid)._update_mail_alias({})

        if cid_changed:
            u.company_id = old_cid
