# -*- coding: utf-8 -*-

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents.mail_documents_activity_data_Inbox")
    util.update_record_from_xml(cr, "documents.mail_documents_activity_data_tv")
    util.update_record_from_xml(cr, "documents.mail_documents_activity_data_md")
