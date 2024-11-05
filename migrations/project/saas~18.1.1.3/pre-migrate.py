from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.create_column(cr, "project_milestone", "sequence", "integer", default=10)
    util.remove_view(cr, "project.project_sharing_portal")
    util.rename_xmlid(cr, *eb("project.project_sharing_{embed,portal}"))
    util.remove_view(cr, "project.project_sharing")
