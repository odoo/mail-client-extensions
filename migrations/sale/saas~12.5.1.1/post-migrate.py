# -*- coding: utf-8 -*-
from ast import literal_eval
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM ir_config_parameter WHERE key='sale.auto_done_setting' RETURNING value")
    if cr.rowcount:
        auto_done, = cr.fetchone()
        try:
            auto_done = literal_eval(auto_done)
        except ValueError:
            pass
        else:
            if auto_done:
                util.env(cr)["res.groups"].browse(util.ref(cr, "base.group_user")).write(
                    {"implied_ids": [(4, util.ref(cr, "sale.group_auto_done_setting"))]}
                )
