# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    for sub_type in ["mt_ticket_task_done", "mt_team_ticket_task_done"]:
        util.if_unchanged(cr, f"helpdesk_fsm.{sub_type}", util.update_record_from_xml)
