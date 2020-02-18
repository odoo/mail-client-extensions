# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "event.type", "default_registration_min")
    util.remove_field(cr, "event.event", "seats_min")
