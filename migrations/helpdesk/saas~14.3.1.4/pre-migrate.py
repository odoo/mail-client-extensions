# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    ticket_rating_id = util.ref(cr, 'helpdesk.mt_ticket_rated')
    cr.execute("UPDATE mail_message_subtype SET description = NULL WHERE id = %s", [ticket_rating_id])
