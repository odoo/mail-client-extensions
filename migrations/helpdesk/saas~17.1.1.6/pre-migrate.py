# -*- coding: utf-8 -*-

from odoo.osv.expression import FALSE_DOMAIN, TRUE_DOMAIN

from odoo.upgrade import util


def migrate(cr, version):
    eb = util.expand_braces
    util.remove_view(cr, "helpdesk.helpdesk_ticket_action_close_analysis_graph_inherit_dashboard")
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_tree"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_kanban"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_activity"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_pivot"))
    util.rename_xmlid(cr, *eb("helpdesk.helpdesk_ticket_action_7days{,_}success_graph"))
    util.remove_record(cr, "helpdesk.helpdesk_ticket_action_7dayssuccess_cohort")
    util.remove_record(cr, "helpdesk.model_helpdesk_ticket_action_share")

    util.create_column(cr, "helpdesk_tag", "_upg_ticket_type_ids", "int[]")
    cr.execute(
        """
            INSERT INTO helpdesk_tag (name, _upg_ticket_type_ids)
                 SELECT name,
                        ARRAY_AGG(id)
                   FROM helpdesk_ticket_type
                  GROUP BY name
            ON CONFLICT (name)
              DO UPDATE
                    SET _upg_ticket_type_ids = EXCLUDED._upg_ticket_type_ids
              RETURNING id,
                        _upg_ticket_type_ids
        """
    )
    ticket_type_ids_per_tag_id = dict(cr.fetchall())
    tag_id_per_ticket_type_id = {}
    for tag_id, ticket_type_ids in ticket_type_ids_per_tag_id.items():
        tag_id_per_ticket_type_id.update((ticket_type_id, tag_id) for ticket_type_id in ticket_type_ids)
    cr.execute(
        """
            INSERT INTO helpdesk_tag_helpdesk_ticket_rel (helpdesk_tag_id, helpdesk_ticket_id)
                 SELECT tag.id,
                        ticket.id
                   FROM helpdesk_ticket ticket
                   JOIN helpdesk_ticket_type type
                     ON type.id = ticket.ticket_type_id
                   JOIN helpdesk_tag tag
                     ON type.id = ANY(tag._upg_ticket_type_ids)
            ON CONFLICT DO NOTHING
        """
    )
    cr.execute(
        """
        INSERT INTO helpdesk_sla_helpdesk_tag_rel (helpdesk_sla_id, helpdesk_tag_id)
             SELECT helpdesk_sla_id,
                    tag.id
               FROM helpdesk_sla_helpdesk_ticket_type_rel sla_ticket
               JOIN helpdesk_tag tag
                 ON sla_ticket.helpdesk_ticket_type_id = ANY(tag._upg_ticket_type_ids)
        ON CONFLICT DO NOTHING
      """
    )
    util.remove_column(cr, "helpdesk_tag", "_upg_ticket_type_ids")

    def ticket_type_to_tags_adapter(leaf, _or, _neg):
        left, op, right = leaf
        if op not in ["in", "not in", "=", "!="]:
            return [leaf]
        REM_DOMAIN = FALSE_DOMAIN if _neg ^ _or else TRUE_DOMAIN
        if isinstance(right, (list, tuple)):
            right = [tag_id_per_ticket_type_id[val] for val in right if val in tag_id_per_ticket_type_id]
            if not right:
                return REM_DOMAIN
        elif isinstance(right, int) and right is not False:
            op = "in" if op == "=" else "not in" if op == "!=" else op
            if right in tag_id_per_ticket_type_id:
                right = [tag_id_per_ticket_type_id[right]]
            else:
                return REM_DOMAIN
        return [(left, op, right)]

    util.domains.adapt_domains(
        cr, "helpdesk.sla.report.analysis", "ticket_type_id", "tag_ids", adapter=ticket_type_to_tags_adapter
    )
    util.remove_field(cr, "helpdesk.sla.report.analysis", "ticket_type_id")
    util.domains.adapt_domains(
        cr, "helpdesk.ticket.report.analysis", "ticket_type_id", "tag_ids", adapter=ticket_type_to_tags_adapter
    )
    util.remove_field(cr, "helpdesk.ticket.report.analysis", "ticket_type_id")
    util.domains.adapt_domains(cr, "helpdesk.sla", "ticket_type_ids", "tag_ids", adapter=ticket_type_to_tags_adapter)
    util.remove_field(cr, "helpdesk.sla", "ticket_type_ids")
    util.domains.adapt_domains(cr, "helpdesk.ticket", "ticket_type_id", "tag_ids", adapter=ticket_type_to_tags_adapter)
    util.remove_field(cr, "helpdesk.ticket", "ticket_type_id")
    util.remove_field(cr, "helpdesk.sla.status", "ticket_type_id")
    util.remove_model(cr, "helpdesk.ticket.type")
