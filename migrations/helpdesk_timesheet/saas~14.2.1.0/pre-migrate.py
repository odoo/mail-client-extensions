# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.ticket", "task_id")
    util.remove_field(cr, "helpdesk.ticket", "_related_task_ids")
    util.remove_field(cr, "helpdesk.ticket", "is_closed")
    util.remove_field(cr, "helpdesk.ticket", "is_task_active")
