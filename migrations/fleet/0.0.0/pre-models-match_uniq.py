# -*- coding: utf-8 -*-
from odoo import models

try:
    import odoo.addons.fleet.models.fleet_vehicle as _ignored  # noqa
except Exception:
    import odoo.addons.fleet.models.fleet as _ignored  # noqa


def migrate(cr, version):
    pass


class VehicleState(models.Model):
    _inherit = "fleet.vehicle.state"
    _module = "fleet"
    _match_uniq = True
