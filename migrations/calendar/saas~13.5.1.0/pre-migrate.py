# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "calendar_event", "follow_recurrence", "boolean", default=False)
