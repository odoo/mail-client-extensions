# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "test_mail.mail_test_ticket_tracking_tpl", util.update_record_from_xml)
    util.if_unchanged(cr, "test_mail.mail_test_container_tpl", util.update_record_from_xml)
