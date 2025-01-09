from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
        WITH fallback_id AS (
            SELECT value::int AS id
              FROM ir_config_parameter
             WHERE key = 'point_of_sale.fallback_nomenclature_id'
        )
        UPDATE pos_config c
           SET fallback_nomenclature_id = f.id
          FROM fallback_id f,
               res_company s
         WHERE s.id = c.company_id
           AND f.id != s.nomenclature_id
           AND c.fallback_nomenclature_id IS NULL
        """
    )
    if util.module_installed(cr, "barcode_gs1_nomenclature"):
        cr.execute(
            """
            WITH not_gs1 AS (
                SELECT id
                  FROM barcode_nomenclature
                 WHERE is_gs1_nomenclature IS NOT TRUE
              ORDER BY id ASC
                 LIMIT 1
            )
            UPDATE pos_config c
               SET fallback_nomenclature_id = not_gs1.id
              FROM not_gs1,
                   res_company s
              JOIN barcode_nomenclature b
                ON b.id = s.nomenclature_id
             WHERE s.id = c.company_id
               AND b.is_gs1_nomenclature IS TRUE
            """
        )
    cr.execute(
        """
        DELETE FROM ir_config_parameter
         WHERE key = 'point_of_sale.fallback_nomenclature_id'
        """
    )
