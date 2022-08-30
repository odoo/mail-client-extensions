# -*- coding: utf-8 -*-
import logging

from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("create index tmp_mig_salesubremoval_speedup_idx on mail_message(id) WHERE model = 'sale.subscription'")
    util.ENVIRON["__created_fk_idx"].append("tmp_mig_salesubremoval_speedup_idx")
