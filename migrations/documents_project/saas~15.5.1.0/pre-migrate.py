# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    for field in ("project_documents_parent_folder", "project_documents_template_folder", "project_use_documents"):
        for model in ("res.company", "res.config.settings"):
            util.remove_field(cr, model, field)

    util.remove_field(cr, "project.project", "company_use_documents")
    util.remove_view(cr, "documents_project.res_config_settings_view_form")
