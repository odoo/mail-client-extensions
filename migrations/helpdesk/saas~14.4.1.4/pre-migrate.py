# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.convert_field_to_html(cr, "helpdesk.team", "description")
    util.convert_field_to_html(cr, "helpdesk.sla", "description")
    util.convert_field_to_html(cr, "helpdesk.ticket", "description")
