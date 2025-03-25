from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents_sign.ir_actions_server_create_sign_template_direct", util.update_record_from_xml)
