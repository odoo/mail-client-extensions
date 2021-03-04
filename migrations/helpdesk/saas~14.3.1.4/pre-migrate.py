# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    ticket_rating_id = util.ref(cr, 'helpdesk.mt_ticket_rated')
    cr.execute("UPDATE mail_message_subtype SET description = NULL WHERE id = %s", [ticket_rating_id])
    util.create_column(cr, "helpdesk_team", "auto_close_ticket", "boolean")
    util.create_column(cr, "helpdesk_team", "auto_close_day", "int4", default=7)
    util.create_m2m(cr, "team_stage_auto_close_from_rel", "helpdesk_team", "helpdesk_stage")
    util.create_column(cr, "helpdesk_team", "to_stage_id", "int4")
