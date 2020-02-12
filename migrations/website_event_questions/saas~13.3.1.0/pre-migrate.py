# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_field(cr, "event.question", "is_individual", "once_per_order")
    cr.execute("UPDATE event_question SET once_per_order = NOT once_per_order")
