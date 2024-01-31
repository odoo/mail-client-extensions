from odoo.upgrade import util


def migrate(cr, version):
    attached_on_sale, attached_on_sale_value = "", ""
    prod_columns = set(util.get_columns(cr, "product_document"))
    if "attached_on_sale" in prod_columns:
        attached_on_sale = ", attached_on_sale"
        attached_on_sale_value = ", 'hidden'"
    common_column_names = [col for col in util.get_columns(cr, "mrp_document") if col in prod_columns]
    common_column_joined = ", ".join(common_column_names)
    util.create_column(cr, "product_document", "_upg_mrp_id", "int4")
    cr.execute(
        f"""
        INSERT INTO product_document (_upg_mrp_id, {common_column_joined}, attached_on_mrp {attached_on_sale})
             SELECT id, {common_column_joined}, 'bom' {attached_on_sale_value}
               FROM mrp_document
          RETURNING _upg_mrp_id,
                    product_document.id
        """
    )
    ids_mapped = dict(cr.fetchall())
    util.remove_column(cr, "product_document", "_upg_mrp_id")
    if ids_mapped:
        util.replace_record_references_batch(cr, ids_mapped, "product.document")
    util.merge_model(cr, "mrp.document", "product.document")
