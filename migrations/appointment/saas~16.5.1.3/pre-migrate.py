# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "appointment_type", "event_videocall_source", "varchar")
