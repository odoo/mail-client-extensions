from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents_sign.documents_sign_template_form_inherit", util.update_record_from_xml)
    util.update_record_from_xml(cr, "documents_sign.ir_actions_server_create_sign_template_direct_create")
    util.update_record_from_xml(cr, "documents_sign.ir_actions_server_create_sign_template_direct")
