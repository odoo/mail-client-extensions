from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "helpdesk.sla.report.analysis", "successful_sla_rate")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "failed_sla_rate")
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ongoing_sla_rate")
    util.remove_record(cr, "helpdesk.helpdesk_sla_report_analysis_filter_status_per_deadline")
    util.remove_record(cr, "helpdesk.helpdesk_sla_report_analysis_filter_stage_failed")

    # If helpdesk stage has no helpdesk teams linked (team_ids = []) then search the
    # eventual tickets linked to that stage to add the team of the ticket to the stage
    # since team_ids will be required.
    query = """
        INSERT INTO team_stage_rel (helpdesk_stage_id, helpdesk_team_id)
             SELECT ticket.stage_id AS helpdesk_stage_id,
                    ticket.team_id AS helpdesk_team_id
               FROM helpdesk_ticket ticket
          LEFT JOIN team_stage_rel ts
                 ON ticket.stage_id = ts.helpdesk_stage_id
              WHERE ts.helpdesk_team_id IS NULL
                AND ticket.team_id IS NOT NULL
                AND ticket.stage_id IS NOT NULL
           GROUP BY ticket.stage_id,
                    ticket.team_id
    """
    cr.execute(query)

    # If some helpdesk stage always has no helpdesk teams linked (team_ids = []) then search
    # the eventual helpdesk SLAs linked to that stage to add the team of the ticket to the stage.
    query = """
        INSERT INTO team_stage_rel (helpdesk_stage_id, helpdesk_team_id)
             SELECT sla.stage_id AS helpdesk_stage_id,
                    sla.team_id AS helpdesk_team_id
               FROM helpdesk_sla sla
          LEFT JOIN team_stage_rel ts
                 ON sla.stage_id = ts.helpdesk_stage_id
              WHERE ts.helpdesk_team_id IS NULL
                AND sla.team_id IS NOT NULL
                AND sla.stage_id IS NOT NULL
           GROUP BY sla.stage_id,
                    sla.team_id
    """
    cr.execute(query)

    # Last way to find a helpdesk team for the remaining helpdesk stage without any helpdesk
    # team linked is the search in the tracking values of stage_id in helpdesk ticket to find a
    # ticket whom was in that stage.
    tracking_fname = "field_id" if util.column_exists(cr, "mail_tracking_value", "field_id") else "field"
    query = util.format_query(
        cr,
        """
        WITH stage_without_team AS (
               SELECT s.id
                 FROM helpdesk_stage s
            LEFT JOIN team_stage_rel ts
                   ON ts.helpdesk_stage_id = s.id
                WHERE ts.helpdesk_team_id IS NULL
        ),
        ticket_stage_tracking AS (
            SELECT t.team_id,
                   mtv.old_value_integer AS old_stage_id,
                   mtv.new_value_integer AS new_stage_id
              FROM helpdesk_ticket t
              JOIN mail_message mm
                ON mm.res_id = t.id
               AND mm.model = 'helpdesk.ticket'
              JOIN mail_tracking_value mtv
                ON mm.id = mtv.mail_message_id
              JOIN ir_model_fields imf
                ON mtv.{tracking_fname} = imf.id
               AND imf.name = 'stage_id'
               AND imf.model = 'helpdesk.ticket'
             WHERE t.team_id IS NOT NULL
        )
        INSERT INTO team_stage_rel (helpdesk_stage_id, helpdesk_team_id)
             SELECT s.id AS helpdesk_stage_id,
                    t.team_id AS helpdesk_team_id
               FROM stage_without_team s
               JOIN ticket_stage_tracking t
                 ON s.id = t.old_stage_id
                 OR s.id = t.new_stage_id
           GROUP BY s.id,
                    t.team_id
        """,
        tracking_fname=tracking_fname,
    )
    cr.execute(query)

    # IF heldesk stage has no helpdesk teams, then remove that stage reference
    # from any heldpesk ticket too.
    cr.execute(
        """
        WITH stages_without_teams AS (
          SELECT s.id
            FROM helpdesk_stage s
       LEFT JOIN team_stage_rel ts
              ON s.id = ts.helpdesk_stage_id
           WHERE ts.helpdesk_team_id IS NULL
        )
        UPDATE helpdesk_ticket t
           SET stage_id = NULL
          FROM stages_without_teams w
         WHERE w.id = t.stage_id
        """
    )
    # If helpdesk stage has no helpdesk teams even with the previous queries
    # then remove it.
    query = """
        -- delete the helpdesk_stage without any helpdesk teams linked.
        WITH stages_without_teams AS (
          SELECT s.id
            FROM helpdesk_stage s
       LEFT JOIN team_stage_rel ts
              ON s.id = ts.helpdesk_stage_id
           WHERE ts.helpdesk_team_id IS NULL
        )
        DELETE
          FROM helpdesk_stage s
         USING stages_without_teams w
         WHERE s.id = w.id
    """
    cr.execute(query)
