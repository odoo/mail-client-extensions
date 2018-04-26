# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    if not util.table_exists(cr, 'web_planner'):
        return
    cr.execute("DELETE FROM web_planner RETURNING view_id")
    for view_id, in cr.fetchall():
        util.remove_view(cr, view_id=view_id)

    util.remove_model(cr, 'web.planner')
    util.remove_module(cr, 'web_planner')
