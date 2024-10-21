from odoo.upgrade import util

documents_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    xmlid_mapping = {
        "documents_approvals_folder": "document_approvals_folder",
    }
    documents_pre_migrate.migrate_folders_xmlid(cr, "documents_approvals", xmlid_mapping)
