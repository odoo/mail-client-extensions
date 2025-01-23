from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("documents_hr_recruitment.ir_actions_server_create_hr_{candidate,applicant}"))
