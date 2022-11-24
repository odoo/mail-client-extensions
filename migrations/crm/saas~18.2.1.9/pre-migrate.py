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
        UPDATE crm_lead lead
           SET (probability, won_status) = (
            CASE WHEN stage.is_won IS TRUE THEN 100
                 ELSE lead.probability
            END,
            CASE WHEN stage.is_won IS TRUE THEN 'won'
                 WHEN lead.active IS NOT True AND lead.probability = 0 THEN 'lost'
                 ELSE 'pending'
            END
          )
          FROM crm_stage stage
         WHERE lead.stage_id = stage.id
    """
    util.explode_execute(cr, query, table="crm_lead", alias="lead")
