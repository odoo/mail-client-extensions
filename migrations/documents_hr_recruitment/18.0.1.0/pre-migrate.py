from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        SELECT 1
          FROM documents_document hr,
               documents_document recr
         WHERE hr.id = %s
           AND hr.active
           AND recr.id = %s
           AND recr.active
           AND recr.id::text != ALL(STRING_TO_ARRAY(hr.parent_path, '/'))
           AND recr.folder_id IS NULL
        """,
        [
            util.ref(cr, "documents_hr.document_hr_folder"),
            util.ref(cr, "documents_hr_recruitment.document_recruitment_folder"),
        ],
    )
    if cr.rowcount:
        util.update_record_from_xml(
            cr, "documents_hr_recruitment.document_recruitment_folder", fields=("folder_id", "internal_access")
        )
