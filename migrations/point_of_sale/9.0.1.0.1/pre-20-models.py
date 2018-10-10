# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "pos.config", "cash_control", "boolean")
    cr.execute("UPDATE pos_config SET cash_control=true")
