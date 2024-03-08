# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # Share by pre-cowed-layout.
    views_to_reset = util.ENVIRON.get("website_cowed_views_to_reset", set())
    for xmlid in views_to_reset:
        util.reset_cowed_views(cr, xmlid)
