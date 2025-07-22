from odoo.upgrade import util


def migrate(cr, version):
    # remove duplicates before we add the UNIQUE(code, name) constraint, and reassign the remaining NCM code to products
    cr.execute(
        """
        WITH duplicates AS (
            SELECT ARRAY_AGG(ncm.id ORDER BY imd IS NULL, ncm.id) AS ids
              FROM l10n_br_ncm_code ncm
         LEFT JOIN ir_model_data imd
                ON imd.model = 'l10n_br.ncm.code' AND imd.res_id = ncm.id
          GROUP BY ncm.code, ncm.name
            HAVING count(*) > 1
        ),

        _ AS (
            UPDATE product_template pt
               SET l10n_br_ncm_code_id = d.ids[1]
              FROM duplicates d
             WHERE pt.l10n_br_ncm_code_id = ANY(d.ids[2:])
        )

        DELETE FROM l10n_br_ncm_code
              USING duplicates d
              WHERE id = ANY(d.ids[2:])
        """
    )

    # fill the name and code fields, they're required after the migration
    for field in ("name", "code"):
        query = util.format_query(
            cr,
            "UPDATE l10n_br_ncm_code SET {0} = id::text WHERE {0} IS NULL",
            field,
        )
        util.explode_execute(cr, query, table="l10n_br_ncm_code")
