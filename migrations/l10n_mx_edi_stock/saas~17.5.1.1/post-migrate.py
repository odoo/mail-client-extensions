from odoo.upgrade import util


def migrate(cr, version):
    # Only if `l10n_mx_edi_stock_extended` used to be installed:
    if util.column_exists(cr, "product_template", "l10n_mx_edi_hazardous_material_code"):
        # Migrate `l10n_mx_edi_hazardous_material_code` to `l10n_mx_edi_hazardous_material_code_id`.
        # This can only be done in post-migrate as we need the new data of `l10n_mx_edi.hazardous_material_code`.
        cr.execute("""
             UPDATE product_template
                SET l10n_mx_edi_hazardous_material_code_id = h.id
               FROM l10n_mx_edi_hazardous_material h
              WHERE h.code = product_template.l10n_mx_edi_hazardous_material_code
                AND COALESCE(product_template.l10n_mx_edi_hazardous_material_code, '') != ''
        """)

        # Get a list of products whose code could not be migrated.
        cr.execute("""
             SELECT id, default_code, name, l10n_mx_edi_hazardous_material_code
               FROM product_template
              WHERE COALESCE(l10n_mx_edi_hazardous_material_code, '') != ''
                AND l10n_mx_edi_hazardous_material_code_id IS NULL
        """)
        products_migration_failed = cr.fetchall()

        if products_migration_failed:
            # Create an 'invalid' hazardous material to set on products that couldn't be migrated.
            # That way, the product is still marked as hazardous, though the user needs to fix the code.
            cr.execute("""
                INSERT INTO l10n_mx_edi_hazardous_material (code, name)
                     VALUES ('INVALID', 'Unknown hazardous')
                  RETURNING id
            """)
            (hazardous_material_id,) = cr.fetchall()

            cr.execute(
                """
                INSERT INTO ir_model_data (module, name, res_id, model)
                     VALUES ('__upgrade__', 'l10n_mx_unknown_hazardous_material', %s, 'l10n_mx_edi.hazardous.material')
                """,
                [hazardous_material_id],
            )

            cr.execute(
                """
                 UPDATE product_template
                    SET l10n_mx_edi_hazardous_material_code_id = %s
                  WHERE COALESCE(l10n_mx_edi_hazardous_material_code, '') != ''
                    AND l10n_mx_edi_hazardous_material_code_id IS NULL
                """,
                [hazardous_material_id],
            )

            products_migration_failed = [
                (id, "{}{}".format((default_code and f"[{default_code}] ") or "", name), hazmat_code)
                for id, default_code, name, hazmat_code in products_migration_failed
            ]

            message = """
                <details>
                <summary>
                    The available Mexican hazardous material codes are now loaded in Odoo.
                    Some of your products had an invalid hazardous material code.
                    After the migration, these have been assigned the code
                    'INVALID - Unknown hazardous'.
                    You should either (1) fix the codes on the products and then delete the
                    code 'INVALID - Unknown hazardous', or
                    (2) fix the codes on the products before migrating and re-do the migration
                    (in which case the code 'INVALID - Unknown hazardous' will not be created).
                </summary>
                List of products with invalid hazardous material codes:
                <ul>
                    {}
                </ul>
                </details>
            """.format(
                "\n".join(
                    f"""
                    <li>
                        {util.get_anchor_link_to_record("product.template", id, display_name)}
                        (code: {hazmat_code})
                    </li>
                    """
                    for id, display_name, hazmat_code in products_migration_failed
                )
            )
            util.add_to_migration_reports(message=message, category="Accounting", format="html")

        util.remove_field(cr, "product.template", "l10n_mx_edi_hazardous_material_code")
