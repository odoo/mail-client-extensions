# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    Contract = util.env(cr)["hr.contract"].with_context(_mig_dry_run=False)
    util.recompute_fields(cr, Contract, ["final_yearly_costs"])
