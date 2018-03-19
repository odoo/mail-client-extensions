# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    util.create_column(cr, 'helpdesk_team', 'active', 'boolean')
    cr.execute("UPDATE helpdesk_team SET active=true")

    util.remove_model(cr, 'helpdesk.ticket.merge')
