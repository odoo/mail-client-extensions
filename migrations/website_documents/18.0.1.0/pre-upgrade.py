from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "documents_document", "website_id", "int4")
    query = """
        UPDATE documents_document d
           SET website_id = c.website_id
          FROM res_company c
         WHERE c.id = d.company_id
           AND c.website_id IS NOT NULL
           AND {parallel_filter}
    """
    util.explode_execute(cr, query, table="documents_document", alias="d")
