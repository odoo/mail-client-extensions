# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.delete_unused(cr, "hr_fleet.onboarding_fleet_training")
