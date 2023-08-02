# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "event_sale.event_report_template_full_page_ticket_inherit_sale")
