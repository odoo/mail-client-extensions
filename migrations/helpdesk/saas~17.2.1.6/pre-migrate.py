# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    old = util.ref(cr, "helpdesk.mail_act_helpdesk_handle")
    new = util.ref(cr, "mail.mail_activity_data_todo")

    util.replace_record_references_batch(cr, {old: new}, "mail.activity.type", replace_xmlid=False)
    util.remove_record(cr, "helpdesk.mail_act_helpdesk_handle")
