# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_migration_of_fresh_module(cr, "timesheet_grid")
