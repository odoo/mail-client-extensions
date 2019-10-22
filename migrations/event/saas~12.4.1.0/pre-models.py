# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "event_type", "sequence", "int4")
    cr.execute("UPDATE event_type SET sequence = id")
