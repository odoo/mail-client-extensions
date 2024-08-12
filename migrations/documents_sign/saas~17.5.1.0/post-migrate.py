from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "documents_sign.documents_sign_template_form_inherit", util.update_record_from_xml)
