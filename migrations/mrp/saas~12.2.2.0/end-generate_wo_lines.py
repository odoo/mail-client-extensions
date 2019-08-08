# -*- coding: utf-8 -*-
from operator import itemgetter
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    WO = util.env(cr)["mrp.workorder"]
    cr.execute("SELECT id FROM mrp_workorder")
    ids = list(map(itemgetter(0), cr.fetchall()))
    for wo in util.iter_browse(WO, ids):
        if "_generate_wo_lines" in dir(wo):
            wo._generate_wo_lines()
        else:
            wo.generate_wo_lines()
