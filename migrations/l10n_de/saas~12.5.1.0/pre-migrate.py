# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    de = "bw by be bb hb hh he mv ni nw rp sl sn st sh th"
    for state in de.split():
        util.remove_record(cr, "l10n_de.state_de_" + state)
