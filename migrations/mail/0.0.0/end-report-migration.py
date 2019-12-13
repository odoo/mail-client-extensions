# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if len(util.migration_reports):
        util.announce_migration_report(cr)
