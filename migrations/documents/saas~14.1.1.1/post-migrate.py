# -*- coding:utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    """
    upgrade script for Master documents onboarding adjustements.
    ENT PR: 12720
    """

    # bypass noupdate documents_data
    util.if_unchanged(cr, "documents.documents_internal_folder", util.update_record_from_xml)
    util.if_unchanged(cr, "documents.documents_finance_folder", util.update_record_from_xml)

    # bypass noupdate workflow_data
    if all(util.ref(cr, f"documents.documents_internal_status_{s}") for s in {"inbox", "validated"}):
        util.if_unchanged(cr, "documents.documents_rule_internal_legal", util.update_record_from_xml)
    if all(util.ref(cr, f"documents.documents_internal_status_{s}") for s in {"inbox", "tc"}) and util.ref(
        cr, "documents.documents_finance_folder"
    ):
        util.if_unchanged(cr, "documents.documents_rule_internal_mark", util.update_record_from_xml)

    # bypass noupdate files_data
    if all(util.ref(cr, f"documents.documents_internal_{s}") for s in {"folder", "status_inbox"}):
        util.if_unchanged(cr, "documents.documents_mail_png", util.update_record_from_xml)
