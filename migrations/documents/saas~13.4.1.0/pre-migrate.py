# -*- coding: utf-8 -*-
from odoo.upgrade import util


def migrate(cr, version):
    # models
    util.create_column(cr, "documents_workflow_rule", "has_owner_activity", "boolean")

    # data
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("documents.documents_internal_status_{draft,inbox}"))
    util.delete_unused(cr, "documents.documents_internal_knowledge_quality")
    util.rename_xmlid(cr, *eb("documents.documents_rule_internal_{afv,legal}"))
    util.remove_record(cr, "documents.documents_workflow_action_validate")
    util.remove_record(cr, "documents.documents_rule_internal_validate")
