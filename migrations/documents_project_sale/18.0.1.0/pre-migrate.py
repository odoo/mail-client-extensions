from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.rename_xmlid(cr, *eb("documents_project_sale.{documents_folder,documents_renovations_projects}"))
    util.rename_xmlid(cr, *eb("documents_project_sale.documents_folder_{facet_1_tag_1,tag_unsorted}"))
    util.rename_xmlid(cr, *eb("documents_project_sale.documents_folder_{facet_1_tag_2,tag_in_use}"))
    util.rename_xmlid(cr, *eb("documents_project_sale.documents_folder_{facet_1_tag_3,tag_done}"))
