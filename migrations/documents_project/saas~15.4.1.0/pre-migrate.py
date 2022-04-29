# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "project_project", "use_documents", "boolean")
    util.create_column(cr, "project_project", "documents_folder_id", "int4")
    cr.execute(
        f"""
        UPDATE project_project pp
           SET use_documents = true, documents_folder_id = rc.project_folder
          FROM res_company rc
         WHERE pp.company_id = rc.id
           AND rc.documents_project_settings = true
         {"AND pp.is_fsm = True" if util.column_exists(cr, "project_project", "is_fsm") else ""}
        """
    )

    util.create_m2m(cr, "project_documents_tag_rel", "project_project", "documents_tag")
    cr.execute(
        """
        INSERT INTO project_documents_tag_rel (project_project_id, documents_tag_id)
             SELECT pp.id, pt.documents_tag_id
               FROM project_project pp
               JOIN project_tags_table pt ON pt.res_company_id = pp.company_id
              WHERE pp.use_documents = true
        """
    )

    for model in ("res.company", "res.config.settings"):
        util.remove_field(cr, model, "project_folder")
        util.remove_field(cr, model, "project_tags")
        util.rename_field(cr, model, "documents_project_settings", "project_use_documents")
    cr.execute("DROP TABLE IF EXISTS project_tags_table CASCADE")
