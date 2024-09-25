from odoo.upgrade import util


def migrate(cr, version):
    util.rename_xmlid(cr, "documents_hr.documents_hr_documents_payslips", "documents_hr.documents_tag_payslips")
