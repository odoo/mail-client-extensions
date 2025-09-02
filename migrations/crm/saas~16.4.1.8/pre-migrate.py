from odoo.upgrade import util


def migrate(cr, version):
    util.remove_field(cr, "crm.lead.lost", "set_reason")

    cr.execute(
        """
        UPDATE crm_team
           SET lead_properties_definition = (
                SELECT jsonb_agg(
                  CASE WHEN def ? 'view_in_kanban'
                       THEN def - 'view_in_kanban' || jsonb_build_object('view_in_cards', def->'view_in_kanban')
                       ELSE def
                   END
           )      FROM jsonb_array_elements(lead_properties_definition) AS elem(def)
        )
         WHERE jsonb_path_exists(lead_properties_definition, '$[*]."view_in_kanban"')
        """
    )
