# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    # event-online requirements
    util.update_record_from_xml(cr, "website_event_sale.registration_template")
