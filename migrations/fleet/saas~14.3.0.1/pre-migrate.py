# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "fleet.vehicle.model", "manager_id")
    util.change_field_selection_values(cr, "fleet.vehicle.log.services", "state", {"todo": "new"})
