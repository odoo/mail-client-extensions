# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "event_sale.view_event_registration_ticket_form",
                      "event_sale.event_registration_ticket_view_form")
