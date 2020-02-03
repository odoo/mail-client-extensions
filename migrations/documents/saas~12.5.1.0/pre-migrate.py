# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.force_noupdate(cr, "documents.documents_hr_documents_appraisal")
    util.create_column(cr, "documents_folder", "user_specific", "boolean")

    util.remove_field(cr, "documents.workflow.rule", "criteria_tag_ids")

    util.remove_model(cr, "documents.workflow.tag.criteria")
