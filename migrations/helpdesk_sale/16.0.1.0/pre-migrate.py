# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_view(cr, "helpdesk_sale.helpdesk_ticket_view_form_inherit_sale_user")
