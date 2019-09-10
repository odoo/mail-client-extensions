# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    eb = util.expand_braces

    cr.execute("""
        CREATE TABLE documents_document(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            active boolean,
            thumbnail bytea,
            partner_id integer,
            owner_id integer,
            lock_uid integer,
            file_size integer,
            res_model varchar,
            name varchar,
            type varchar,
            folder_id integer,
            attachment_id integer
        )
    """)

    fname_col = 'name' if util.version_gte('saas~12.4') else 'datas_fname'
    cr.execute("""
        INSERT INTO documents_document
        (id, attachment_id, active, partner_id, owner_id, lock_uid, file_size, res_model, name, type, folder_id)
            SELECT id, id, active, partner_id, owner_id, lock_uid, file_size, res_model, %s, 'binary', folder_id
              FROM ir_attachment
             WHERE folder_id IS NOT NULL OR id IN (SELECT ir_attachment_id FROM document_tag_rel)
    """ % (fname_col,))
    cr.execute("SELECT setval('documents_document_id_seq', (SELECT MAX(id)+1 FROM documents_document))")

    util.rename_field(cr, 'documents.folder', 'attachment_ids', 'document_ids')
    util.rename_field(cr, 'documents.share', 'attachment_ids', 'document_ids')

    util.create_column(cr, 'documents_workflow_rule', 'sequence', 'int4')
    cr.execute("UPDATE documents_workflow_rule set sequence=10")

    util.rename_xmlid(cr, *eb("documents.{documents_,}settings_action"))
    util.rename_xmlid(cr, *eb("documents.document{s,}_view_kanban"))
    util.rename_xmlid(cr, *eb("documents.document{s,}_view_form"))
    util.rename_xmlid(cr, *eb("documents.configuration{,_action}"))
    util.rename_xmlid(cr, *eb("documents.documents_internal_status{_folder,}"))
    util.rename_xmlid(cr, *eb("documents.documents_internal_knowledge{_facet,}"))
    util.rename_xmlid(cr, *eb("documents.documents_internal_template{_facet,}"))
    util.rename_xmlid(cr, *eb("documents.documents_finance_status{_folder,}"))
    util.rename_xmlid(cr, *eb("documents.documents_finance_{Documents_folder,documents}"))
    util.rename_xmlid(cr, *eb("documents.documents_finance_{Fiscal_year_folder,fiscal_year}"))
    util.rename_xmlid(cr, *eb("documents.documents_hr_documents{_facet,}"))
    util.rename_xmlid(cr, *eb("documents.documents_marketing_assets{_facet,}"))
    util.rename_xmlid(cr, *eb("documents.documents_internal_knowledge_{S,s}ales"))
    util.rename_xmlid(cr, *eb("documents.documents_internal_template_{P,p}resentations"))

    cr.execute("""ALTER TABLE document_tag_rel RENAME TO document_tag_rel_old""")
    util.create_m2m(cr, "document_tag_rel", "documents_document", "documents_tag")
    cr.execute("""
        INSERT INTO document_tag_rel (documents_document_id, documents_tag_id)
        SELECT ir_attachment_id, documents_tag_id FROM document_tag_rel_old
    """)
    cr.execute("DROP TABLE document_tag_rel_old")

    util.remove_view(cr, "documents.documents_view_search_inherit")
    util.remove_view(cr, "documents.inherit_mail_attachment_view_kanban")
    util.remove_view(cr, "documents.documents_view_kanban")
    util.remove_view(cr, "documents.documents_view_form")
    util.remove_view(cr, "documents.documents_upload_url_view")
    util.remove_view(cr, "documents.documents_view_list")
