# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.env(cr)["ir.config_parameter"].set_param("hr_fleet.delay_alert_contract", 15)
