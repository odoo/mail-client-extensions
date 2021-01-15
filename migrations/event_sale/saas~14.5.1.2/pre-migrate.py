# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "event_sale.event_registration_report_template_badge")
    util.remove_view(cr, "event_sale.event_event_report_template_badge")
