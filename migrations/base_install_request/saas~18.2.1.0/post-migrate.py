from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "base_install_request.mail_template_base_install_request", util.update_record_from_xml)
