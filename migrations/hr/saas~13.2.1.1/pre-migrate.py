# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "hr_employee", "departure_date", "date")
    util.create_column(cr, "hr_departure_wizard", "departure_date", "date")
    util.create_column(cr, "hr_departure_wizard", "archive_private_address", "boolean")
    util.remove_field(cr, "hr.departure.wizard", "plan_id")
