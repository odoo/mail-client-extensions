from odoo.upgrade import util


def migrate(cr, version):
    if util.column_exists(cr, "product_document", "attached_on_sale"):
        attached_on_sale = util.ColumnList.from_unquoted(cr, ["attached_on_sale"]).using(leading_comma=True)
        attached_on_sale_value = util.SQLStr(", 'hidden'")
    else:
        attached_on_sale = attached_on_sale_value = util.SQLStr("")

    columns = util.get_common_columns(
        cr, "product_document", "mrp_document", ignore=["id", "attached_on_sale", "attached_on_mrp"]
    )

    util.create_column(cr, "product_document", "_upg_mrp_id", "int4")

    query = util.format_query(
        cr,
        """
        INSERT INTO product_document (_upg_mrp_id, {common_column_joined}, attached_on_mrp {attached_on_sale})
             SELECT id, {common_column_joined}, 'bom' {attached_on_sale_value}
               FROM mrp_document
          RETURNING _upg_mrp_id,
                    product_document.id
        """,
        common_column_joined=columns,
        attached_on_sale=attached_on_sale,
        attached_on_sale_value=attached_on_sale_value,
    )
    cr.execute(query)
    ids_mapped = dict(cr.fetchall())
    util.remove_column(cr, "product_document", "_upg_mrp_id")
    if ids_mapped:
        util.replace_record_references_batch(cr, ids_mapped, "mrp.document", "product.document")
    util.merge_model(cr, "mrp.document", "product.document")
