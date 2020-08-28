# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.rename_xmlid(cr, "quality_control.quality_alert_view_search", "quality.quality_alert_view_search")
