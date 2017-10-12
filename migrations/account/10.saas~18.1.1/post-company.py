# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for company in util.env(cr)['res.company'].search([]):
        company.create_op_move_if_non_existant()
