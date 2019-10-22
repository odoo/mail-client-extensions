# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sign_template", "privacy", "varchar")
    cr.execute("UPDATE sign_template SET privacy = 'invite'")
