# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.recompute_fields(cr, "res.currency", ["decimal_places"])
