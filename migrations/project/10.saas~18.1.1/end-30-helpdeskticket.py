# -*- coding: utf-8 -*-
import json
import logging
from math import ceil, log10
import os

from odoo.addons.base.maintenance.migrations import util

_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.hepdesk.saas-18." + __name__)


def migrate(cr, version):
    if util.table_exists(cr, "project_issue") and os.environ.get("ODOO_MIG_S18_HELPDESK_ISSUES"):
        L = _logger.debug

        env = util.env(cr)
        Projects = env["project.project"]
        HelpdeskTeam = env["helpdesk.team"]

        nosplit = os.environ.get("ODOO_MIG_S18_HELPDESK_ISSUES", "")
        if nosplit:
            project_filter = "AND p.id NOT IN %s"
            params = [tuple(int(s) for s in nosplit.split(","))]
        else:
            project_filter, params = "", []

        for model in ["project_issue", "helpdesk_stage", "helpdesk_tag", "helpdesk_ticket"]:
            util.create_column(cr, model, "_tmp", "int4")

        L("copy projects with issues to helpdesk team")
        created_teams = {}
        cr.execute(
            """
            SELECT p.id, p.label_issues
              FROM project_project p
             WHERE EXISTS(SELECT 1 FROM project_issue WHERE project_id = p.id)
            {0}
        """.format(
                project_filter
            ),
            params,
        )

        for pid, label in cr.fetchall():
            project = Projects.browse(pid)
            name = u"%s (%s)" % (project.name, label)
            nid = HelpdeskTeam.create(
                {"name": name, "description": label, "company_id": project.company_id.id, "color": project.color}
            ).id
            cr.execute("UPDATE project_issue SET _tmp=%s WHERE project_id=%s", [nid, pid])
            created_teams[pid] = nid

        if created_teams:
            cr.execute(
                """
                UPDATE ir_translation
                   SET name = 'helpdesk.ticket,description',
                       res_id = ('{}'::jsonb->>res_id::varchar)::int4
                 WHERE name = 'project.project,label_issues'
                   AND res_id IN %s
            """.format(
                    json.dumps(created_teams)
                ),
                [tuple(created_teams.keys())],
            )

        cr.execute(
            """
            WITH new_stages AS (
                INSERT INTO helpdesk_stage(_tmp, name, sequence, fold)
                SELECT id, name, sequence, fold FROM project_task_type
                where id in (select distinct(stage_id) from project_issue)
                RETURNING id, _tmp
            )
            INSERT INTO team_stage_rel(helpdesk_team_id, helpdesk_stage_id)
                SELECT i._tmp, s.id
                    FROM project_task_type_rel p,
                         new_stages s,
                         project_issue i
                    WHERE s._tmp = p.type_id
                    AND i.project_id = p.project_id
                    GROUP BY i._tmp, s.id
        """
        )

        L("assign tags")
        cr.execute(
            """
            INSERT INTO helpdesk_tag(_tmp, name, color)
                 SELECT t.id, t.name, t.color
                   FROM project_tags t
                WHERE EXISTS(SELECT 1 FROM project_issue_project_tags_rel s
                 WHERE s.project_issue_id in (select id from project_issue)
                 AND s.project_tags_id = t.id)
        """
        )

        ignore = ("id", "_tmp", "team_id", "stage_id")
        columns = set(util.get_columns(cr, "helpdesk_ticket", ignore)) & set(
            util.get_columns(cr, "project_issue", ignore)
        )  # noqa:E127

        cr.execute(
            """
            select greatest(
                (select max(id) from helpdesk_ticket),
                (select max(id) from project_issue),
                2   -- at least offset 10
            )
        """
        )
        (maxid,) = cr.fetchone()
        offset = 10 ** ceil(log10(maxid))
        util.announce(
            cr,
            "11.0",
            "Issues have their id offset of %s" % offset,
            header=None,
            footer=None,
            pluses_for_enterprise=False,
        )

        L("convert issues to hepdesk ticket (id offset %s)", offset)

        helpdesk_ticket_type = util.ref(cr, "helpdesk.type_incident")

        cr.execute(
            """
            INSERT INTO helpdesk_ticket(id,
                                        team_id,
                                        ticket_type_id,
                                        partner_email,
                                        assign_date,
                                        assign_hours,
                                        close_date,
                                        close_hours,
                                        deadline,
                                        stage_id,
                                        access_token,
                                        {columns})
            SELECT i.id + %s, i._tmp, {ticket_type}, i.email_from, i.date_open,
                   i.working_hours_open, i.date_closed, i.working_hours_close,
                   i.date_deadline, s.id,
                   md5(md5(random()::varchar || i.id::varchar) || clock_timestamp()::varchar)::uuid::varchar,
                   {select_columns}
            FROM project_issue i
            LEFT JOIN helpdesk_stage s ON i.stage_id = s._tmp
        """.format(
                columns=",".join(columns),
                select_columns=",".join(["i.%s" % c for c in columns]),
                ticket_type=helpdesk_ticket_type,
            ),
            [offset],
        )

        cr.execute(
            """
            INSERT INTO helpdesk_tag_helpdesk_ticket_rel(helpdesk_ticket_id, helpdesk_tag_id)
                SELECT project_issue_id + %s, t.id
                FROM project_issue_project_tags_rel p,
                     helpdesk_tag t
                WHERE t._tmp = p.project_tags_id
        """,
            [offset],
        )

        for ir in util.indirect_references(cr, bound_only=True):
            L("update references: %r", ir)
            upd = ""
            if ir.res_model:
                upd += "{ir.res_model} = 'helpdesk.ticket',"
            if ir.res_model_id:
                upd += "{ir.res_model_id} = (SELECT id FROM ir_model WHERE model='helpdesk.ticket'),"
            upd = upd.format(ir=ir)
            whr = ir.model_filter(placeholder="'project.issue'")

            query = """
                UPDATE "{ir.table}"
                   SET {upd}
                       "{ir.res_id}" = "{ir.res_id}" + %s
                 WHERE {whr}
                   AND COALESCE("{ir.res_id}", 0) != 0
            """.format(
                **locals()
            )

            cr.execute(query, [offset])

        L("update reference fields")
        cr.execute("SELECT model, name FROM ir_model_fields WHERE ttype='reference'")
        for model, column in cr.fetchall():
            table = util.table_of_model(cr, model)
            if util.column_exists(cr, table, column):
                cr.execute(
                    """UPDATE "{table}"
                                 SET "{column}" = 'helpdesk.ticket,' || ((substr("{column}", 14))::integer + %s)
                               WHERE "{column}" LIKE 'project.issue,%%'
                           """.format(
                        table=table, column=column
                    ),
                    [offset],
                )

        L("change sequence & helpdesk ticket priority")
        cr.execute("SELECT max(id) + 1 FROM helpdesk_ticket")
        cr.execute("ALTER SEQUENCE helpdesk_ticket_id_seq RESTART WITH %s", cr.fetchone())
        cr.execute("UPDATE helpdesk_ticket SET priority='3' WHERE priority='2'")

        L("change mail.message.subtype")
        subtypes = {}
        for mt in "new stage".split():
            subtypes[util.ref(cr, "project.mt_issue_" + mt)] = util.ref(cr, "helpdesk.mt_ticket_" + mt)
            subtypes[util.ref(cr, "project.mt_project_issue_" + mt)] = util.ref(cr, "helpdesk.mt_team_ticket_" + mt)

        util.replace_record_references_batch(cr, subtypes, "mail.message.subtype", replace_xmlid=False)

        L("reassign other records model")
        model_issue = env["ir.model"]._get_id("project.issue")
        model_ticket = env["ir.model"]._get_id("helpdesk.ticket")

        cr.execute(
            """
            UPDATE mail_alias a
               SET alias_parent_thread_id = t.team_id
              FROM helpdesk_ticket t, ir_model m, ir_model p
             WHERE m.id = a.alias_model_id
               AND m.model = 'helpdesk.ticket'
               AND p.id = a.alias_parent_model_id
               AND p.model = 'helpdesk.team'
               AND t._tmp = a.alias_force_thread_id
        """
        )
        cr.execute("UPDATE mail_alias SET alias_model_id=%s WHERE alias_model_id=%s", [model_ticket, model_issue])

        if util.table_exists(cr, "rating_rating"):
            cr.execute(
                """
                UPDATE rating_rating r
                   SET parent_res_id = t.team_id
                  FROM helpdesk_ticket t
                 WHERE r.res_model = 'helpdesk.ticket'
                   AND r.parent_res_model = 'helpdesk.team'
                   AND t._tmp = r.res_id
            """
            )

        cr.execute(
            """
            UPDATE ir_act_server
               SET model_id = %s,
                   model_name = 'helpdesk.ticket'
             WHERE model_id = %s
        """,
            [model_ticket, model_issue],
        )
        cr.execute(
            "UPDATE ir_act_server SET binding_model_id=%s WHERE binding_model_id=%s", [model_ticket, model_issue]
        )

        cr.execute(
            """
            WITH _u AS (
                UPDATE ir_act_server
                   SET crud_model_id = %s
                 WHERE crud_model_id = %s
             RETURNING id
            )
            UPDATE ir_server_object_lines l
               SET col1 = t.id
              FROM ir_model_fields i,
                   ir_model_fields t
             WHERE server_id IN (select id FROM _u)
               AND i.id = l.col1
               AND t.model = 'helpdesk.ticket'
               AND t.name = i.name
        """,
            [model_ticket, model_issue],
        )

        if util.table_exists(cr, "base_automation"):
            cr.execute(
                """
                UPDATE base_automation
                   SET trg_date_id = (SELECT id
                                        FROM ir_model_fields
                                       WHERE model='helpdesk.ticket'
                                         AND name='write_date')
                 WHERE trg_date_id = (SELECT id
                                        FROM ir_model_fields
                                       WHERE model='project.issue'
                                         AND name='date_action_last')
            """
            )

        util.update_field_references(cr, "date_action_last", "write_date", only_models=["helpdesk.ticket"])

        cr.execute("UPDATE ir_filters SET model_id='helpdesk.ticket' WHERE model_id='project.issue'")
        cr.execute(
            "UPDATE mail_template SET model='helpdesk.ticket', model_id=%s WHERE model='project.issue'", [model_ticket]
        )

        for model in ["project_issue", "helpdesk_stage", "helpdesk_tag", "helpdesk_ticket"]:
            util.remove_column(cr, model, "_tmp")
