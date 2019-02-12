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
            folder_id integer
        )
    """)

    cr.execute("""
        INSERT INTO documents_document
        (id, attachment_id, active, thumbnail, partner_id, owner_id, lock_uid, file_size, res_model, name, type, folder_id)
            SELECT id, id, active, thumbnail, partner_id, owner_id, lock_uid, file_size, res_model, coalesce(attachment_name, datas_fname), 'binary', folder_id
              FROM ir.attachment
             WHERE folder_id IS NOT NULL
    """)
    cr.execute("SELECT setval('documents_document_id_seq', (SELECT MAX(id)+1 FROM documents_document))")

    util.rename_field(cr, 'documents.folder', 'attachment_ids', 'document_ids')
    util.rename_field(cr, 'documents.share', 'attachment_ids', 'document_ids')

    util.create_column(cr, 'documents_workflow_rule', 'sequence', 'int4')
    cr.execute("UPDATE documents_workflow_rule set sequence=10")

    util.rename_xmlid(cr, eb("documents.{documents_,}settings_action"))
    util.rename_xmlid(cr, eb("documents.{documents_view_search_inherit,document_view_search}"))
    util.rename_xmlid(cr, eb("documents.document{s,}_view_kanban"))
    util.rename_xmlid(cr, eb("documents.document{s,}_view_form"))
    util.rename_xmlid(cr, eb("documents.configuration{,_action}"))
