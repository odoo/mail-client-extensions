# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_field_references(cr, "date_open", "create_date", only_models=("event.registration",))
    util.remove_field(cr, "event.registration", "date_open")
