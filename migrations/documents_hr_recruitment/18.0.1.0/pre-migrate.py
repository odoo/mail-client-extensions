from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents_hr_recruitment.document_recruitment_folder", util.update_record_from_xml)
