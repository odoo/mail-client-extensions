import logging

from psycopg2 import sql
from psycopg2.extras import Json

from odoo.tools.sql import make_index_name, rename_column

from odoo.upgrade import util

NS = "openerp.addons.base.maintenance.migrations.base.17.5."
_logger = logging.getLogger(NS + __name__)


def migrate(cr, version):
    # migrate company dependent field
    # create column "ir_model_fields"."company_dependent" as the identifier of indirect reference
    util.create_column(cr, "ir_model_fields", "company_dependent", "boolean")

    # 1. rename ir_property to _ir_property as a backup
    # In operations such as `merge_model`, _ir_property is considered as a table belonging to a model
    # due to its foreign keys, which act as direct references. However, since the referenced model doesn't exist,
    # this would result in an error. To prevent this, we drop the foreign keys here.
    cr.execute("""
                  ALTER TABLE ir_property
                    RENAME TO _ir_property;
                  ALTER TABLE _ir_property
    DROP CONSTRAINT IF EXISTS ir_property_company_id_fkey,
    DROP CONSTRAINT IF EXISTS ir_property_fields_id_fkey,
    DROP CONSTRAINT IF EXISTS ir_property_create_uid_fkey,
    DROP CONSTRAINT IF EXISTS ir_property_write_uid_fkey;
    """)

    # 2. special case for product.category.property_xxx
    if util.module_installed(cr, "stock_account"):
        cleanup_stock_account_property(cr)

    # 3. migrate data to the table jsonb column
    # warning:
    # if the field was not stored but not company dependent and still had company_dependent data in ir_property
    # upgrade_company_dependent_field may create redundant jsonb column for it
    cr.execute(
        """
        SELECT DISTINCT imf.id, imf.model, imf.name, imf.ttype, imf.relation
          FROM _ir_property AS ip
          JOIN ir_model_fields AS imf
            ON ip.fields_id = imf.id
           AND imf.store IS NOT TRUE
           -- ignore some fields handled in their own modules
           AND (imf.model, imf.name) NOT IN (
               ('planning.slot.template', 'project_id')  -- no more company dependent since saas-17.1
              ,('res.partner', 'property_product_pricelist')
              )
      ORDER BY imf.model
        """
    )
    tables_with_many2one_company_dependent = set()
    company_dependent_field_ids = set()
    for field_id, model_name, field_name, field_type, field_relation in cr.fetchall():
        upgrade_company_dependent_field(cr, model_name, field_name, field_id, field_type, field_relation)
        company_dependent_field_ids.add(field_id)
        if field_type == "many2one":
            tables_with_many2one_company_dependent.add(util.table_of_model(cr, model_name))
    if tables_with_many2one_company_dependent:
        # ANALYZE table to make the index to be used while dealing with indirect_reference
        cr.execute(
            util.format_query(
                cr,
                "ANALYZE " + ", ".join("{}" for _ in tables_with_many2one_company_dependent),
                *tables_with_many2one_company_dependent,
            )
        )
    # ir_model_fields.company_dependent is an identifier for indirect reference
    # we leave other columns to be synced by ORM
    if company_dependent_field_ids:
        cr.execute(
            "UPDATE ir_model_fields SET company_dependent = TRUE WHERE id = ANY(%s)",
            [list(company_dependent_field_ids)],
        )

    # 4. special case for res_partner.property_product_pricelist
    if util.module_installed(cr, "product"):
        # post upgrade field res.partner.property_product_pricelist
        # promise the column specific_property_product_pricelist and its index
        # exist for the product/0.0.0/pre-sanitize-pricelist.py
        upgrade_property_product_pricelist(cr)

    # 5. migrate ir_model_data and backup _ir_model_data for model='ir.property'
    cr.execute(
        """
        UPDATE ir_model_data imd
           SET res_id = d.id,
               model = 'ir.default'
          FROM ir_default d
          JOIN _ir_property p
            ON d.company_id IS NOT DISTINCT FROM p.company_id
           AND d.field_id = p.fields_id
           AND p.res_id IS NULL -- it meant default value in ir_property
         WHERE imd.model = 'ir.property'
           AND imd.res_id = p.id
        """
    )
    cr.execute("CREATE TABLE _ir_model_data (LIKE ir_model_data INCLUDING ALL)")
    cr.execute(
        """
        INSERT INTO _ir_model_data SELECT * FROM ir_model_data WHERE model = 'ir.property';
        DELETE FROM ir_model_data WHERE model = 'ir.property';
        """
    )

    # 6. remove model ir.property
    util.remove_record(cr, "base.ir_property_form")
    util.remove_model(cr, "ir.property")


def cleanup_stock_account_property(cr):
    # When product_category.with_company(company_id).property_valuation != 'real_time', its ir_property specification for all stock
    # account property fields can be removed to reduce the number of NOT NULL values after upgrade
    # It is acceptable after FIX odoo/180034

    # the fallback installed by default is 'manual_periodic' for all companies
    # but we still check it here in case it is customized by the customer
    cr.execute(
        """
        WITH property_valuation_fallbacks AS (
            SELECT company_id,
                   value_text
              FROM _ir_property p
              JOIN ir_model_fields f
                ON f.id = p.fields_id
               AND f.model = 'product.category'
               AND f.name = 'property_valuation'
               AND p.res_id IS NULL
        )
        SELECT ARRAY_AGG(rc.id)
          FROM res_company rc
     LEFT JOIN property_valuation_fallbacks pvfc
            ON pvfc.company_id = rc.id
     LEFT JOIN property_valuation_fallbacks pvfn
            ON pvfn.company_id IS NULL
         WHERE COALESCE(pvfc.value_text, pvfn.value_text, '') != 'real_time'
        """
    )
    # company_ids whose fallback for product.category.property_valuation is not 'real_time'
    [non_real_time_fallback_company_ids] = cr.fetchone() or [[]]

    cr.execute(
        """
        WITH specified_property_valuation AS (
            SELECT res_id,
                   company_id,
                   value_text AS property_valuation
              FROM _ir_property p
              JOIN ir_model_fields f
                ON f.id = p.fields_id
               AND f.model = 'product.category'
               AND f.name = 'property_valuation'
               AND p.company_id IS NOT NULL
               AND p.res_id IS NOT NULL
        ), to_delete AS (
            SELECT p.id
              FROM _ir_property p
              JOIN ir_model_fields f
                ON f.id = p.fields_id
               AND f.model = 'product.category'
               AND f.name IN (
                       'property_stock_account_input_categ_id',
                       'property_stock_account_output_categ_id',
                       'property_stock_valuation_account_id',
                       'property_stock_account_production_cost_id'
                   )
               AND p.res_id IS NOT NULL
               AND p.company_id IS NOT NULL
         LEFT JOIN specified_property_valuation spv
                ON p.res_id = spv.res_id
               AND p.company_id = spv.company_id
             WHERE COALESCE(spv.property_valuation, '') != 'real_time'
                OR (spv.res_id IS NULL AND p.company_id = ANY(%s))
        )
        DELETE FROM _ir_property p
               USING to_delete d
               WHERE p.id = d.id
        """,
        [non_real_time_fallback_company_ids],
    )


def upgrade_company_dependent_field(cr, model_name, field_name, field_id, field_type, field_relation):
    """migrate data for a company dependent field fromm ir_property to its jsonb column"""
    # store_type: the corresponding SQL type for value to be stored in jsonb
    # property_value_field: column name which stores the data of the old company dependent field
    join_comodel = sql.SQL("")
    if field_type == "boolean":
        store_type = sql.SQL("boolean")
        property_value_field = sql.SQL("prop.value_integer")
    elif field_type == "integer":
        store_type = sql.SQL("numeric")
        property_value_field = sql.SQL("prop.value_integer")
    elif field_type == "float":
        store_type = sql.SQL("numeric")
        property_value_field = sql.SQL("prop.value_float")
    elif field_type in ("char", "text", "html", "selection"):
        store_type = sql.SQL("text")
        property_value_field = sql.SQL("prop.value_text")
    elif field_type in ("date", "datetime"):
        store_type = sql.SQL("text")
        property_value_field = sql.SQL("prop.value_datetime")
    elif field_type == "many2one":
        store_type = sql.SQL("numeric")
        property_value_field = sql.SQL("comodel.id")
        # join comodel for many2one which SET NULL for references to deleted records
        if field_relation == "_unknown":
            _logger.warning(
                "Skipping many2one company dependent field %s.%s pointing to removed model", model_name, field_name
            )
            return
        join_comodel = sql.SQL(
            util.format_query(
                cr,
                """
                LEFT JOIN {} comodel
                       ON NULLIF(SPLIT_PART(prop.value_reference, ',', 2), '')::int4 = comodel.id
                """,
                util.table_of_model(cr, field_relation),
            )
        )
    else:
        _logger.warning("Unexpected field type %s for %s.%s", field_type, model_name, field_name)
        return

    table_name = util.table_of_model(cr, model_name)
    # it is possible in the old database the column was remained because a mistake of upgrade script
    # it happens especially when the field was a stored non-company_dependent field and later becomes company_dependent
    if util.column_exists(cr, table_name, field_name):
        cr.execute(util.format_query(cr, "DROP INDEX IF EXISTS {}", make_index_name(table_name, field_name)))
        rename_column(cr, table_name, field_name, "_" + field_name)
        _logger.warning(
            (
                "Renamed column `%s` of `%s` to `_%s`. "
                "A new column with previous name now holds the data of company dependent field `%s.%s`"
            ),
            field_name,
            table_name,
            field_name,
            model_name,
            field_name,
        )
    util.create_column(cr, table_name, field_name, "jsonb")

    # upgrade model's table for customized value
    util.explode_execute(
        cr,
        util.format_query(
            cr,
            """
            WITH jsonb_property AS (
                SELECT t.id AS res_id,
                       jsonb_object_agg(prop.company_id::text, ({property_value_field})::{store_type}) AS value
                  FROM _ir_property prop
                    -- join the table already in the CTE to avoid computing
                    -- stuff we won't use in the update below
                  JOIN {table_name} t
                    ON NULLIF(SPLIT_PART(prop.res_id, ',', 2), '')::int4 = t.id
                   AND prop.type = {field_type}
                   AND prop.company_id IS NOT NULL
                   AND prop.res_id IS NOT NULL
                   AND prop.fields_id = {field_id}
                   AND {{parallel_filter}}
                 {join_comodel}
              GROUP BY t.id
            )
            UPDATE {table_name}
               SET {field_name} = jsonb_property.value
              FROM jsonb_property
             WHERE {table_name}.id = jsonb_property.res_id
            """,
            property_value_field=property_value_field,
            store_type=store_type,
            field_type=sql.SQL(cr.mogrify("%s", [field_type]).decode()),
            field_id=sql.SQL(cr.mogrify("%s", [field_id]).decode()),
            join_comodel=join_comodel,
            table_name=table_name,
            field_name=field_name,
        ),
        table=table_name,
        alias="t",
    )

    # add index especially for many2one in case it is used to handle indirect_references
    cr.execute(
        util.format_query(
            cr,
            """
            CREATE INDEX {index_name}
                ON {table_name}
             USING btree(({field_name} IS NOT NULL))
             WHERE {field_name} IS NOT NULL;
            """,
            index_name=make_index_name(table_name, field_name),
            table_name=table_name,
            field_name=field_name,
        )
    )

    # upgrade ir_default for fallback value
    #
    # Previously, in ir_property
    # a row with `res_id IS NULL AND company_id = 1` is the fallback for the company 1
    # a row with `res_id IS NULL AND company_id IS NULL` is the fallback for all companies without the above row
    # if the above 2 rows don't exist, the fallback is logical NULL
    #
    # Now, in the jsonb implementation we cannot store the fallback in the jsonb column of the original table
    # instead, we store it in the ir_default table where a row
    # 1. is a logical default for non-company_dependent fields
    # 2. is a logical fallback for company_dependent fields
    #
    # And now, in ir_default for company_dependent fields.
    # a row with `company_id = 1` is the fallback for the company 1
    # a row with `company_id IS NULL` is the fallback for all companies without the above row
    # if the above 2 rows don't exist, the fallback is logical NULL
    #
    # Note:
    # previously the NULL stored in ir_property.value_xxx will be stored as 'false' in ir_default.json_value
    #
    cr.execute("DELETE FROM ir_default WHERE field_id = %s", [field_id])
    cr.execute(
        util.format_query(
            cr,
            """
            INSERT INTO ir_default(field_id, company_id, json_value)
            SELECT prop.fields_id,
                   prop.company_id,
                   COALESCE(
                       to_jsonb(({property_value_field})::{store_type})::text,
                       'false'
                   )
              FROM _ir_property prop
              {join_comodel}
             WHERE prop.type = %s
               AND prop.fields_id = %s
               AND prop.res_id IS NULL
            """,
            property_value_field=property_value_field,
            store_type=store_type,
            join_comodel=join_comodel,
        ),
        [field_type, field_id],
    )


def upgrade_property_product_pricelist(cr):
    """upgrade the res.partner.property_product_pricelist"""
    # res.partner.property_product_pricelist was a non-stored, non-company_dependent computed field but used ir_property as a hack
    # upgrade_company_dependent_field will move its company dependent values to column "res_partner"."property_product_pricelist"
    # and table "ir_default". Then we move the company dependent specific values to the new field
    # res.partner.specific_property_product_pricelist. And its customized fallback should be stored in the "ir_config_parameter"

    cr.execute(
        """
        SELECT id, model, model_id, ttype, relation
          FROM ir_model_fields
         WHERE model = 'res.partner'
           AND name = 'property_product_pricelist'
        """
    )
    old_field_id, model_name, model_id, field_type, field_relation = cr.fetchone()

    cr.execute(
        """
        INSERT INTO ir_model_fields(
                        model_id, field_description,
                        model, name, ttype,
                        relation, state, store, company_dependent)
             VALUES (%s, %s,
                     'res.partner', 'specific_property_product_pricelist', 'many2one',
                     'product.pricelist', 'base', True, True)
          RETURNING id
        """,
        [model_id, Json({"en_US": "Specific Property Product Pricelist"})],
    )
    [field_id] = cr.fetchone()

    # migrate company dependent data from property_product_pricelist to specific_property_product_pricelist
    cr.execute(
        """
        UPDATE _ir_property
           SET fields_id = %s
         WHERE fields_id = %s
        """,
        [field_id, old_field_id],
    )

    upgrade_company_dependent_field(
        cr, model_name, "specific_property_product_pricelist", field_id, field_type, field_relation
    )

    # move the fallback values to ir_config_parameter
    # ir.config_parameter.value is a required field, use python str(False) text for NULL value
    cr.execute(
        """
        WITH deleted_default AS (
            DELETE FROM ir_default
             WHERE field_id = %s
         RETURNING company_id, json_value
        )
        INSERT INTO ir_config_parameter(key, value)
             SELECT 'res.partner.property_product_pricelist' || COALESCE('_' || company_id::text, ''),
                    CASE WHEN json_value = 'false' THEN 'False' ELSE json_value END
               FROM deleted_default
        """,
        [field_id],
    )
