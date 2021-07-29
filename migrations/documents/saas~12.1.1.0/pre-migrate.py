# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    eb = util.expand_braces

    cr.execute(
        """
        CREATE TABLE documents_document(
            id SERIAL PRIMARY KEY,
            create_uid integer,
            create_date timestamp without time zone,
            write_uid integer,
            write_date timestamp without time zone,
            active boolean,
            partner_id integer,
            owner_id integer,
            lock_uid integer,
            file_size integer,
            res_model varchar,
            name varchar,
            url varchar,
            type varchar,
            folder_id integer,
            attachment_id integer
        )
    """
    )
    cr.execute("INSERT INTO ir_model(name, model) VALUES ('Document', 'documents.document') RETURNING id")
    model_id = cr.fetchone()[0]

    fname_col = "name" if util.version_gte("saas~12.4") else "COALESCE(name, datas_fname)"
    cr.execute(
        """
        INSERT INTO documents_document(id, create_uid, create_date, write_uid, write_date,
                                       attachment_id, active, partner_id, owner_id, lock_uid,
                                       file_size, res_model, name, url, type, folder_id)
             SELECT id, create_uid, create_date, write_uid, write_date,
                    id, active, partner_id, owner_id, lock_uid,
                    file_size, res_model, {}, url, type, folder_id
               FROM ir_attachment
              WHERE folder_id IS NOT NULL
                 OR id IN (SELECT ir_attachment_id FROM document_tag_rel)
    """.format(
            fname_col
        )
    )
    cr.execute("SELECT setval('documents_document_id_seq', (SELECT MAX(id)+1 FROM documents_document))")

    # thumbnail was an attachment on attachments, move them to document
    cr.execute(
        """
        UPDATE ir_attachment
           SET res_model = 'documents.document'
         WHERE res_model = 'ir.attachment'
           AND res_field = 'thumbnail'
           AND res_id IN (SELECT id FROM documents_document)
    """
    )

    util.create_m2m(cr, "documents_document_res_users_rel", "documents_document", "res_users")
    cr.execute(
        """
        INSERT INTO documents_document_res_users_rel(documents_document_id, res_users_id)
             SELECT ir_attachment_id, res_users_id
               FROM ir_attachment_res_users_rel
              WHERE ir_attachment_id IN (SELECT id FROM documents_document)
    """
    )
    cr.execute("DROP TABLE ir_attachment_res_users_rel")

    cr.execute("ALTER TABLE document_tag_rel RENAME TO document_tag_rel_old")
    util.create_m2m(cr, "document_tag_rel", "documents_document", "documents_tag")
    cr.execute(
        """
        INSERT INTO document_tag_rel(documents_document_id, documents_tag_id)
             SELECT ir_attachment_id, documents_tag_id
               FROM document_tag_rel_old
    """
    )
    cr.execute("DROP TABLE document_tag_rel_old")

    cr.execute("SELECT id FROM documents_document")
    ids = {d: d for d, in cr.fetchall()}
    if ids:
        util.replace_record_references_batch(cr, ids, "ir.attachment", "documents.document")

    for field in {
        "thumbnail",
        "folder_id",
        "lock_uid",
        "partner_id",
        "owner_id",
        "favorited_ids",
        "available_rule_ids",
    }:
        util.remove_field(cr, "ir.attachment", field)
    util.remove_field(cr, "ir.attachment", "tag_ids", drop_column=False)
    util.remove_field(cr, "ir.attachment", "active", skip_inherit={"mrp.document"})

    util.remove_inherit_from_model(cr, "ir.attachment", "mail.thread")
    util.remove_inherit_from_model(cr, "ir.attachment", "mail.activity.mixin")

    util.create_m2m(cr, "documents_document_documents_share_rel", "documents_document", "documents_share")
    cr.execute(
        """
        INSERT INTO documents_document_documents_share_rel(documents_document_id, documents_share_id)
             SELECT ir_attachment_id, documents_share_id
               FROM documents_share_ir_attachment_rel
              WHERE ir_attachment_id IN (SELECT id FROM documents_document)
    """
    )
    cr.execute("DROP TABLE documents_share_ir_attachment_rel")

    util.rename_field(cr, "documents.folder", "attachment_ids", "document_ids")
    util.rename_field(cr, "documents.share", "attachment_ids", "document_ids")

    cr.execute(
        """
        UPDATE mail_alias
           SET alias_model_id = %s
         WHERE id IN (SELECT alias_id FROM documents_share)
    """,
        [model_id],
    )

    util.create_column(cr, "documents_workflow_rule", "sequence", "int4")
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

    util.remove_view(cr, "documents.documents_view_search_inherit")
    util.remove_view(cr, "documents.inherit_mail_attachment_view_kanban")
    util.remove_view(cr, "documents.documents_view_kanban")
    util.remove_view(cr, "documents.documents_view_form")
    util.remove_view(cr, "documents.documents_upload_url_view")
    util.remove_view(cr, "documents.documents_view_list")

    for xmlid in ["document_debug_action", "action_url_form", "document_action"]:
        util.force_noupdate(cr, "documents.%s" % xmlid, False)
