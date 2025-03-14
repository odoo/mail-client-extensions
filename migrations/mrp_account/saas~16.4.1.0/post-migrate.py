from odoo.upgrade import util


def migrate(cr, version):
    # Convert the company dependent analytic account id on the BOM to a 100% analytic distribution
    cr.execute("SELECT id FROM ir_model_fields WHERE model = 'mrp.bom' AND name = 'analytic_account_id'")
    old_field_id = cr.fetchone()[0]
    cr.execute("SELECT id FROM ir_model_fields WHERE model = 'mrp.bom' AND name = 'analytic_distribution_text'")
    new_field_id = cr.fetchone()[0]
    query = """
        UPDATE ir_property prop
        SET name = 'analytic_distribution_text',
            type = 'text',
            value_text = jsonb_build_object(right(value_reference, length(value_reference) - strpos(value_reference, ',')), 100.0),
            value_reference = NULL,
            fields_id = %s
        WHERE fields_id = %s
    """
    cr.execute(query, (new_field_id, old_field_id))
    util.remove_field(cr, "mrp.bom", "analytic_account_id")
