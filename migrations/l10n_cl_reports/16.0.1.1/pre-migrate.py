# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_model(cr, "account.eightcolumns.report.cl")
    util.remove_model(cr, "f29.report.wizard")
