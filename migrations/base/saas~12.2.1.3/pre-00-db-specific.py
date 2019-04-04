# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def _openerp(cr, version):
    # This lang is in noupdate because it has a custom code (`ar` instead of `ar_SY`)
    # The name has been reassigned to another lang (ar_AA) with odoo/odoo#28640
    # We cannot force noupdate as, updating the code is forbidden.
    cr.execute(
        "UPDATE res_lang SET name = 'Arabic (Syria) / الْعَرَبيّة' WHERE id = %s", [util.ref(cr, "base.lang_ar_SY")]
    )
    util.remove_view(cr, view_id=11735)  # some website_event view that lost its xmlid
    util.remove_view(cr, view_id=8823)  # this view removed comment on slide views, now a flag on channels
    cr.execute("UPDATE ir_ui_view SET arch_db = replace(arch_db, 'website_published', 'is_published') WHERE id = 8752")


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _openerp})
