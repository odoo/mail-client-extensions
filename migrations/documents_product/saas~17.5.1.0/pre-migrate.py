from odoo.upgrade import util

documents_pre_migrate = util.import_script("documents/saas~17.5.1.4/pre-migrate.py")


def migrate(cr, version):
    util.rename_field(cr, "res.company", "product_tags", "product_tag_ids")
    util.rename_field(cr, "res.config.settings", "product_tags", "product_tag_ids")

    util.rename_field(cr, "res.company", "product_folder", "product_folder_id")
    util.rename_field(cr, "res.config.settings", "product_folder", "product_folder_id")

    xmlid_mapping = {
        "documents_product_folder": "document_product_folder",
    }
    documents_pre_migrate.migrate_folders_xmlid(cr, "documents_product", xmlid_mapping)
