# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.remove_field(cr, "hr.contract", "final_yearly_costs_fte")
