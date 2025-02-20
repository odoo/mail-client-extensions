from odoo.upgrade import util


def migrate(cr, version):
    query = """
        UPDATE sign_item si
           SET name = sit.name->>'en_US'
          FROM sign_item_type sit
         WHERE sit.id = si.type_id
           AND si.name IS NULL
        """
    util.parallel_execute(cr, util.explode_query_range(cr, query, table="sign_item", alias="si"))
