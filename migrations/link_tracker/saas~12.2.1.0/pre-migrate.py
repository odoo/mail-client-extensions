# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM link_tracker_code WHERE code IS NULL")
    util.remove_field(cr, "link.tracker.click", "click_date")
