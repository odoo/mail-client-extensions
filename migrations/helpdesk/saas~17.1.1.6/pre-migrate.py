# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "helpdesk.model_helpdesk_ticket_action_share")
