# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.ENVIRON["no_model_data_delete"].update(
        {
            "fleet.vehicle.model.brand": "unused",
            "fleet.vehicle.model": "unused",
        }
    )
