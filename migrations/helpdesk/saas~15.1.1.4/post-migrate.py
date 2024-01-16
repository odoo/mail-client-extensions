# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # https://github.com/odoo/enterprise/pull/25461
    util.if_unchanged(cr, "helpdesk.helpdesk_portal_ticket_rule", util.update_record_from_xml)

    ticket_seq_id = util.ref(cr, "helpdesk.seq_helpdesk_ticket")
    seq_name = "ir_sequence_%03d" % ticket_seq_id
    cr.execute("SELECT setval(%s, nextval('helpdesk_ticket_id_seq'))", [seq_name])
