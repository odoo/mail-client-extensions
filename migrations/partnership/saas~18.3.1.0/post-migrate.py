from odoo.upgrade import util


def migrate(cr, version):
    if not util.column_exists(cr, "res_partner", "_upg_membership_product_id"):
        # partnership could be freshly installed, we need this only if membership was installed
        return

    # update the membership product and assign a new grade
    query = """
        WITH new_grades AS (
            INSERT INTO res_partner_grade (name, active, sequence)
                 SELECT p.name,
                        p.active,
                        p.id
                   FROM product_template p
                  WHERE membership = true
                    AND {parallel_filter}
              RETURNING id, sequence AS pid
        ), _updated AS (
            UPDATE product_template p
               SET grade_id = new_grades.id,
                   service_tracking = 'partnership',
                   type = 'service'
              FROM new_grades
             WHERE p.id = new_grades.pid
         RETURNING grade_id
        )
        UPDATE res_partner_grade g
           SET sequence = 10
          FROM _updated
         WHERE g.id = _updated.grade_id
    """
    util.explode_execute(cr, query, table="product_template", alias="p")

    # update the partners to assign the new grades linked to the membership product
    query = """
        UPDATE res_partner r
           SET grade_id = grade.id
          FROM res_partner_grade grade
          JOIN product_template pt
            ON pt.grade_id = grade.id
         WHERE r._upg_membership_product_id = pt.id
           AND COALESCE(r.membership_stop > NOW() at time zone 'UTC', true)
           AND COALESCE(r.membership_start < NOW() at time zone 'UTC', true)
           AND r.membership_state NOT IN ('none', 'canceled', 'old')
           AND r.grade_id IS NULL
    """

    util.explode_execute(cr, query, table="res_partner", alias="r")

    util.remove_column(cr, "product_template", "membership")
    util.remove_column(cr, "product_template", "_upg_membership_product_id")
    util.remove_column(cr, "res_partner", "membership_start")
    util.remove_column(cr, "res_partner", "membership_stop")
    util.remove_column(cr, "res_partner", "membership_state")
