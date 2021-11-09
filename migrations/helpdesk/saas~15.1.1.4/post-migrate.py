# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):

    ticket_seq_id = util.ref(cr, "helpdesk.seq_helpdesk_ticket")
    seq_name = "ir_sequence_%03d" % ticket_seq_id
    cr.execute("SELECT setval(%s, nextval('helpdesk_ticket_id_seq'))", [seq_name])
