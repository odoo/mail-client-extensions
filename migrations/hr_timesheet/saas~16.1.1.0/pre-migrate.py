# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "res.config.settings", "reminder_manager_allow", "reminder_allow")
