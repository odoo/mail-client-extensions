from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "documents.folder", "product_template_ids")
    util.remove_field(cr, "product.template", "documents_allowed_company_id")
    util.remove_field(cr, "product.template", "project_template_use_documents")
    util.remove_field(cr, "product.template", "template_folder_id")
    util.remove_view(cr, "documents_project_sale.product_template_form_view_inherit_documents_project_sale")
