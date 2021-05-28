# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.move_field_to_module(cr, "helpdesk.ticket", "commercial_partner_id", "helpdesk_sale", "helpdesk")
    util.remove_field(cr, "helpdesk.ticket", "is_self_assigned")
