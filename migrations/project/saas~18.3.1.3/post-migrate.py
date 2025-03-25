from odoo.upgrade import util


def migrate(cr, version):
    util.if_unchanged(cr, "project.rating_project_request_email_template", util.update_record_from_xml)
