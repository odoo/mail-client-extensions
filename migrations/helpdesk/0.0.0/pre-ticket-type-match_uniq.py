# -*- coding: utf-8 -*-
from odoo import models
from odoo.addons.helpdesk.models import helpdesk  # noqa


def migrate(cr, version):
    pass


class TicketType(models.Model):
    _inherit = 'helpdesk.ticket.type'
    _module = "helpdesk"
    _match_uniq = True
