from odoo.upgrade import util


def migrate(cr, version):
    util.update_record_from_xml(cr, "documents_hr_recruitment.ir_actions_server_create_hr_applicant")
