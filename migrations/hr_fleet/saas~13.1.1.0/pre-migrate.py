# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "mobility_card", "varchar")
    util.create_column(cr, "fleet_vehicle", "mobility_card", "varchar")
