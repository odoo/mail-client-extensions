# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    # NOTE: See the commit message for an explaination about the reason this script exists.
    if not (util.on_CI() and util.version_gte("13.0")):
        return

    cr.execute("SELECT demo FROM ir_module_module WHERE name='base'")
    if not cr.fetchone()[0]:
        # runbot also try to upgrade without demo data
        return

    p4d = util.ref(cr, "product.product_product_4d")
    if p4d:
        # Record already exists.
        return

    required_columns = {
        "base_unit_count": "1",
    }
    for col in list(required_columns):
        if not util.column_exists(cr, "product_product", col):
            del required_columns[col]

    extra_columns = extra_values = ""
    if required_columns:
        extra_columns = "," + ",".join(required_columns)
        extra_values = "," + ",".join(required_columns.values())

    # Use SQL as the models are not yet in the registry
    cr.execute(
        """
            WITH p4d AS (
                INSERT INTO product_product(
                    product_tmpl_id, default_code, active, combination_indices, weight, can_image_variant_1024_be_zoomed
                    {extra_columns}
                ) VALUES(%s, 'DESK0004', true, '2,4', 0.01, false {extra_values})
                ON CONFLICT (product_tmpl_id, combination_indices) WHERE (active IS true) DO UPDATE SET weight = excluded.weight
                RETURNING id
            )
            INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
            SELECT 'product', 'product_product_4d', 'product.product', id, false
              FROM p4d
        """.format(
            **locals()
        ),
        [util.ref(cr, "product.product_product_4_product_template")],
    )

    util.env(cr).registry.loaded_xmlids.add("product.product_product_4d")
