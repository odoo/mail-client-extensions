# -*- coding: utf-8 -*-
from odoo import models
import odoo.addons.fleet.models.fleet_vehicle as _ignored  # noqa


def migrate(cr, version):
    pass


class VehicleState(models.Model):
    _inherit = "fleet.vehicle.state"
    _module = "fleet"
    _match_uniq = True
