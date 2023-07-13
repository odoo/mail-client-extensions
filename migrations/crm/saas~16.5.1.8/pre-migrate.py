# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead", "calendar_event_count")
