# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "website_event_sale.access_event_event_ticket_public")
    util.remove_record(cr, "website_event_sale.event_event_ticket_public")
    util.remove_view(cr, "website_event_sale.index")
    util.remove_view(cr, "website_event_sale.registration_complete_inherit_website_event_sale")
