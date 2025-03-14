from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "hr_recruitment_extract.hr_recruitment_extract_endpoint")

    iap_extract = util.import_script("iap_extract/saas~16.2.1.0/end-migrate.py")
    iap_extract.migrate_status_code(cr, "hr.applicant")
    iap_extract.migrate_document_uuid(cr, "hr.applicant")
