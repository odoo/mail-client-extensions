# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_column(cr, "gamification_badge_user_wizard", "user_id")  # field still there
