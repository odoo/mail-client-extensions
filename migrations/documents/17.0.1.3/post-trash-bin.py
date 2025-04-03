from os import getenv

from odoo.upgrade import util


def migrate(cr, version):
    unarchive = util.str2bool(getenv("ODOO_UPG_17_UNARCHIVE_DOCUMENTS", "1"))

    if unarchive:
        cr.execute("SELECT 1 FROM documents_document WHERE active IS NOT TRUE FETCH FIRST ROW ONLY")
        if not cr.rowcount:
            # no inactive document, nothing to do
            return

        facet_xmlid = "documents.documents_internal_status"
        facet_id = util.ref(cr, facet_xmlid)
        if not facet_id:
            util.update_record_from_xml(cr, facet_xmlid, ensure_references=True)
            facet_id = util.ref(cr, facet_xmlid)

        cr.execute(
            """
                INSERT INTO documents_tag (facet_id, folder_id, name, create_date, sequence)
                     SELECT id, folder_id, '{"en_US": "Archived"}'::jsonb, now() at time zone 'UTC', 10
                       FROM documents_facet
                      WHERE id = %s
                  RETURNING id
            """,
            [facet_id],
        )
        [tag_id] = cr.fetchone()

        query = cr.mogrify(
            """
            INSERT INTO document_tag_rel (documents_tag_id, documents_document_id)
            SELECT %s, id
              FROM documents_document
             WHERE active IS NOT TRUE
            """,
            [tag_id],
        ).decode()
        util.explode_execute(cr, query, table="documents_document")

        util.explode_execute(
            cr,
            "UPDATE documents_document SET active = true WHERE active IS NOT TRUE",
            table="documents_document",
        )

        util.add_to_migration_reports(
            """
                In Odoo 17, the archived documents are deleted after 30 days. To avoid a loss of documents, we unarchived the archived ones.
                To help you retrieve the archived documents, we created a new tag 'Archived' in the documents module.
            """,
            category="Documents",
            format="md",
        )

    else:
        # keep documents inactive but change write_date to avoid them being deleted immediately
        how_many = util.explode_execute(
            cr,
            "UPDATE documents_document SET write_date = now() at time zone 'UTC' WHERE active is not true",
            table="documents_document",
        )

        if how_many:
            menu_id = util.ref(cr, "documents.menu_root")
            trash_url = f"/web#model=documents.document&view_type=kanban&menu_id={menu_id}&folder_id=TRASH"
            util.add_to_migration_reports(
                f"""
                    In Odoo 17, the archived documents are deleted after 30 days. This delay can be changed in the settings.
                    Please review the content of the [document trash bin]({trash_url}) and unarchive the documents that need to be kept.
                """,
                category="Documents",
                format="md",
            )
