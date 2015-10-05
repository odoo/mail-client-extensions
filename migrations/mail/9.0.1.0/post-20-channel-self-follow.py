# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    for chan in util.env(cr)['mail.channel'].search([], limit=None):
        chan.message_subscribe(channel_ids=[chan.id])
