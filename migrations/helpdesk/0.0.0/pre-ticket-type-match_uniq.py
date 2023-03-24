# -*- coding: utf-8 -*-
from odoo import models

from odoo.addons.base.maintenance.migrations import util

if not util.version_gte("saas~17.1"):
    try:
        from odoo.addons.helpdesk.models import helpdesk_ticket_type  # noqa
    except ImportError:
        from odoo.addons.helpdesk.models import helpdesk  # noqa

    class TicketType(models.Model):
        _inherit = "helpdesk.ticket.type"
        _module = "helpdesk"
        _match_uniq = True


def migrate(cr, version):
    pass
