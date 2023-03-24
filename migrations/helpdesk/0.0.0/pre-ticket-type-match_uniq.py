# -*- coding: utf-8 -*-
from odoo import models

try:
    from odoo.addons.helpdesk.models import helpdesk_ticket_type  # noqa
except ImportError:
    from odoo.addons.helpdesk.models import helpdesk  # noqa


def migrate(cr, version):
    pass


class TicketType(models.Model):
    _inherit = "helpdesk.ticket.type"
    _module = "helpdesk"
    _match_uniq = True
