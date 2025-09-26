from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_share", "website_id", "int4")
    query = """
        UPDATE documents_share s
           SET website_id = c.website_id
          FROM documents_folder f
          JOIN res_company c
            ON c.id = f.company_id
         WHERE f.id = s.folder_id
           AND c.website_id IS NOT NULL
           AND {parallel_filter}
    """
    util.explode_execute(cr, query, table="documents_share", alias="s")
