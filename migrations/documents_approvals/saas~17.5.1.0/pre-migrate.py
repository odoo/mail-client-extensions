from odoo.upgrade import util

documents_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    cr.execute(
        """
           UPDATE ir_model_data AS imd
              SET res_id = d.id,
                  model = 'documents.document',
                  name = 'document_approvals_folder'
             FROM documents_document d
            WHERE imd.module = 'documents_approvals'
              AND imd.model = 'documents.folder'
              AND imd.name = 'documents_approvals_folder'
              AND d._upg_old_folder_id = imd.res_id
        """,
    )

    xmlid_mapping = {
        "documents_approvals_folder": "document_approvals_folder",
    }
    documents_pre_migrate.migrate_folders_xmlid(cr, "documents_approvals", xmlid_mapping)
