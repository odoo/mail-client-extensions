# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("SELECT id FROM ir_act_window_view WHERE view_mode = 'qweb'")
    act_window_view_ids = [r[0] for r in cr.fetchall()]
    util.remove_records(cr, "ir.actions.act_window.view", act_window_view_ids)
    util.remove_view(cr, "website.report_viewhierarchy_children")
    util.remove_view(cr, "website.view_view_qweb")
