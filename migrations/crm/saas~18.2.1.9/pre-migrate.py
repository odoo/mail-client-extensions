from odoo.upgrade import util


def migrate(cr, version):
    # move 'won_status' from enterprise or compute it
    if util.module_installed(cr, "crm_enterprise"):
        util.move_field_to_module(cr, "crm.lead", "won_status", "crm_enterprise", "crm")
        util.move_field_to_module(cr, "crm.activity.report", "won_status", "crm_enterprise", "crm")
    else:
        util.create_column(cr, "crm_lead", "won_status", "varchar")
    # anyway force recompute as heuristic changed: force all won leads to 100%
    # probability, set status (won -> stage, lost -> archived with proba 0)
    query = """
        UPDATE crm_lead l
           SET probability = 100
          FROM crm_stage s
         WHERE s.id = l.stage_id
           AND s.is_won IS TRUE
           AND l.probability != 100
    """
    util.explode_execute(cr, query, table="crm_lead", alias="l")
    query = """
        WITH won_status AS (
            SELECT l.id,
                   CASE WHEN s.is_won IS TRUE THEN 'won'
                        WHEN l.active IS NOT True AND l.probability = 0 THEN 'lost'
                        ELSE 'pending'
                    END as value
              FROM crm_lead l
              JOIN crm_stage s
                ON s.id = l.stage_id
             WHERE {parallel_filter}
        )
        UPDATE crm_lead l
           SET won_status = ws.value
          FROM won_status ws
         WHERE ws.id = l.id
           AND l.won_status IS DISTINCT FROM ws.value
    """
    util.explode_execute(cr, query, table="crm_lead", alias="l")
