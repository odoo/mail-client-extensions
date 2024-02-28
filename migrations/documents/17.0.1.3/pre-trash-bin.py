from odoo.upgrade import util


def migrate(cr, version):
    how_many = util.explode_execute(
        cr,
        "UPDATE documents_document SET write_date = now() at time zone 'UTC' WHERE active is not true",
        table="documents_document",
    )

    if how_many:
        trash_url = "web#model=documents.document&view_type=kanban&folder_id=TRASH"
        util.add_to_migration_reports(
            f"""
                In Odoo 17, the archived documents are deleted after 30 days. This delay can be changed in the settings.
                Please review the content of the [document trash bin]({trash_url}) and unarchive the documents that need to be kept.
            """,
            category="Documents",
            format="md",
        )
