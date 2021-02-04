# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "documents.workflow.rule", "has_business_option")
    util.create_column(cr, "documents_workflow_rule", "link_model", "varchar")
    util.create_column(cr, "documents_document", "is_editable_attachment", "bool")
