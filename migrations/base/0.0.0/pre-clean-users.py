# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~11.5"):
        user_id = util.ref(cr, "base.user_admin")
        if not user_id:
            user_id = util.ensure_xmlid_match_record(cr, "base.user_admin", "res.users", {"login": "admin"})
        if user_id:
            util.force_noupdate(cr, "base.user_admin")

    if util.version_between("10.0", "saas~18.2"):
        util.ensure_xmlid_match_record(cr, "base.default_user", "res.users", {"login": "default"})
