from odoo.upgrade import util

documents_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    util.rename_xmlid(
        cr, "documents_hr.documents_recruitment_plans_tag", "documents_hr.documents_tag_recruitment_reserve"
    )
    util.rename_xmlid(cr, "documents_hr.documents_recruitment_sheet_tag", "documents_hr.documents_tag_cancelled")
    documents_pre_migrate.migrate_folders_xmlid(
        cr,
        "documents_hr_recruitment",
        {
            "documents_recruitment_folder": "document_recruitment_folder",
        },
    )
