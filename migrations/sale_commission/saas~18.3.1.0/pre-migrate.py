from odoo.upgrade import util


def migrate(cr, version):
    need_upgrade = not util.column_exists(cr, "sale_commission_achievement", "add_user_id")
    if need_upgrade:
        # This upgrade script adapts the achievement record. If the sale_commission_linked_achievement
        # was installed, the records have been already updated manually to follow the new specification.
        util.create_column(cr, "sale_commission_achievement", "achieved", "numeric")
        util.create_column(cr, "sale_commission_achievement", "add_user_id", "int4")
        util.create_column(cr, "sale_commission_achievement", "reduce_user_id", "int4")
        query = """
            WITH achievement_commission_lines AS (
                SELECT
                        sca.id AS sca_id,
                        scpu.id AS scpu_id,
                        sca.currency_rate * sca.amount * scpa.rate AS achieved
                  FROM sale_commission_achievement sca
                  JOIN sale_commission_plan scp ON scp.company_id = sca.company_id
                  JOIN sale_commission_plan_achievement scpa ON scpa.plan_id = scp.id
                  JOIN sale_commission_plan_user scpu ON scpu.plan_id = scp.id
                 WHERE sca.type = scpa.type
                   AND CASE
                       WHEN scp.user_type = 'person' THEN sca.user_id = scpu.user_id
                       ELSE sca.team_id = scp.team_id
                   END
            )
            UPDATE sale_commission_achievement a
               SET add_user_id=l.scpu_id,
                   achieved=l.achieved
              FROM achievement_commission_lines l
             WHERE a.id=l.sca_id
        """
        cr.execute(query)
    util.remove_field(cr, "sale.commission.report", "team_id")
    util.remove_field(cr, "sale.commission.achievement", "type")
    util.remove_field(cr, "sale.commission.achievement", "user_id")
    util.remove_field(cr, "sale.commission.achievement", "team_id")
    util.remove_field(cr, "sale.commission.achievement", "amount")
    util.remove_view(cr, "sale_commission.sale_commission_achievement_link_view_list")
