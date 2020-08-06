# -*- coding: utf-8 -*-
from odoo.upgrade import util
from odoo import SUPERUSER_ID


def migrate(cr, version):
    util.remove_view(cr, "pos_blackbox_be.assets")
    minfin_user = util.ref(cr, "pos_blackbox_be.fdm_minfin_user")
    if minfin_user:
        util.replace_record_references_batch(cr, {minfin_user: SUPERUSER_ID}, model="res.users", replace_xmlid=False)
    util.remove_record(cr, "pos_blackbox_be.fdm_minfin_user")
