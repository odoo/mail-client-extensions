from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents_hr.mail_template_document_folder_link", util.update_record_from_xml)
