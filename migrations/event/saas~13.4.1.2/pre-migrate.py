# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.event", "color")
    util.delete_unused(cr, "event.event_type_data_online")
