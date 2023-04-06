# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_usage(cr, "event.registration", "date_open", "create_date")
    util.remove_field(cr, "event.registration", "date_open")
