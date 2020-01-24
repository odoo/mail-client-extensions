# -*- coding: utf-8 -*-
from operator import itemgetter

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("SELECT id FROM pos_order WHERE currency_rate IS NULL")
    ids = list(map(itemgetter(0), cr.fetchall()))
    util.recompute_fields(cr, "pos.order", fields=["currency_rate"], ids=ids)
