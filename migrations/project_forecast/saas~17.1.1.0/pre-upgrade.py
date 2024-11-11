from psycopg2 import sql

from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(
        cr, "planning_slot_template", "project_id", "int4", fk_table="project_project", on_delete_action="SET NULL"
    )
    ir_property = "_ir_property" if util.version_gte("saas~17.5") else "ir_property"

    company_filter = "true"
    cr.execute("SELECT 1 FROM project_project WHERE company_id IS NULL LIMIT 1")
    if not cr.rowcount:
        # no project is accessible to all companies, we can limit to the companies having projects
        cr.execute("SELECT company_id FROM project_project GROUP BY company_id")
        if cr.rowcount:
            cids = tuple(c for (c,) in cr.fetchall())
            company_filter = cr.mogrify("d.company_id IN %s", [cids]).decode()

    cols = util.get_columns(cr, "planning_slot_template", ignore=("id", "project_id"))

    query = util.format_query(
        cr,
        """
        WITH props AS (
            SELECT t.id,
                   COALESCE(jp.id, jd.id) AS project_id,
                   row_number() OVER (PARTITION BY t.id ORDER BY COALESCE(jp.id, jd.id)) AS rn
              FROM planning_slot_template t
              JOIN {p} d
                ON d.fields_id = (SELECT id FROM ir_model_fields WHERE model = 'planning.slot.template' AND name = 'project_id')
               AND d.res_id IS NULL  -- default for properties
              JOIN project_project jd
                ON jd.id = SPLIT_PART(d.value_reference, ',', 2)::int4
               AND d.value_reference LIKE 'project.project,%'
         LEFT JOIN {p} p
                ON p.fields_id = d.fields_id
               AND p.company_id = d.company_id
               AND SPLIT_PART(p.res_id, ',', 2)::int4 = t.id
               AND p.res_id LIKE 'planning.slot.template,%'
              JOIN project_project jp
                ON jp.id = SPLIT_PART(p.value_reference, ',', 2)::int4
               AND d.value_reference LIKE 'project.project,%'
             WHERE {company_filter}
        ),
        -- pick as company of the existing slot the first matched above
        _update AS (
            UPDATE planning_slot_template t
               SET project_id = p.project_id
              FROM props p
             WHERE p.id = t.id
               AND p.rn = 1
        )
        -- duplicate the slot for any extra company
        INSERT INTO planning_slot_template({cols}, project_id)
             SELECT {cols_select}, p.project_id
               FROM planning_slot_template t
               JOIN props p
                 ON p.id = t.id
              WHERE p.rn != 1
        """,
        p=ir_property,
        company_filter=sql.SQL(company_filter),
        cols=cols,
        cols_select=cols.using(alias="t"),
    )
    cr.execute(query)
