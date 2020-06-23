# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "crm_helpdesk.access_helpdesk_ticket_sale_user")
    util.remove_record(cr, "crm_helpdesk.access_helpdesk_stage_sale_user")
