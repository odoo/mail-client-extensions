# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.remove_field(cr, "hr.contract", "type_id")
    util.remove_model(cr, "hr.contract.type")
