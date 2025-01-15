from odoo.upgrade import util


def migrate(cr, version):
    env = util.env(cr)
    env["res.company"].search([("documents_project_folder_id", "=", False)]).documents_project_folder_id = util.ref(
        cr, "documents_project.document_project_folder"
    )
