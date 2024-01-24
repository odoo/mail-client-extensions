# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents.documents_document_write_rule")
    util.if_unchanged(
        cr,
        "documents.mail_template_document_request",
        util.update_record_from_xml,
        reset_translations={"subject", "body_html"},
    )
    util.if_unchanged(
        cr, "documents.digest_tip_documents_0", util.update_record_from_xml, reset_translations={"tip_description"}
    )
