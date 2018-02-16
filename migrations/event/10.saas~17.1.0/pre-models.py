# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.remove_field(cr, 'event.type', 'use_reply_to')
    util.remove_field(cr, 'event.type', 'default_reply_to')
    util.remove_field(cr, 'event.event', 'reply_to')
