# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "hr_contract", "active", "boolean")
    util.create_column(cr, "hr_contract", "reported_to_secretariat", "boolean")
    cr.execute("UPDATE hr_contract SET active=true, reported_to_secretariat=true")
