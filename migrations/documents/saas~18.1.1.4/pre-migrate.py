from odoo.upgrade import util


def migrate(cr, version):
    # Replace Odoobot by False
    cr.execute("ALTER TABLE documents_document ALTER COLUMN owner_id DROP NOT NULL")
    util.explode_execute(
        cr,
        cr.mogrify(
            """
        UPDATE documents_document
           SET owner_id = NULL
         WHERE owner_id = %s
           AND {parallel_filter}
            """,
            [util.ref(cr, "base.user_root")],
        ).decode(),
        table="documents_document",
        alias="documents_document",
    )

    util.rename_field(cr, "documents.document", "is_pinned_folder", "is_company_root_folder")
    util.remove_column(cr, "documents_document", "is_company_root_folder")
