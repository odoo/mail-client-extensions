# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
            WITH form_views AS (
                INSERT INTO ir_ui_view(active, type, mode, priority, arch_db, name, key)
                     SELECT
                        true,
                        'qweb',
                        'primary',
                        16,
                        v.arch_db,
                        CONCAT('website_helpdesk.team_form_', t.id),
                        CONCAT('website_helpdesk.team_form_', t.id)
                       FROM helpdesk_team t,
                            ir_ui_view v
                       JOIN ir_model_data d ON d.model = 'ir.ui.view' AND d.res_id = v.id
                      WHERE d.module = 'website_helpdesk'
                        AND d.name = 'ticket_submit_form'
                        AND t.use_website_helpdesk_form = true
                        AND t.website_form_view_id IS NULL
                  RETURNING id, SUBSTR(name, 28)::integer AS team_id
            )
             UPDATE helpdesk_team t
                SET website_form_view_id = v.id
               FROM form_views AS v
              WHERE t.id = v.team_id
        """
    )

    cr.execute(
        """
             INSERT INTO ir_model_data(module, name, model, res_id, noupdate)
             SELECT 'website_helpdesk', CONCAT('team_form_', id), 'ir.ui.view', website_form_view_id, true
               FROM helpdesk_team
              WHERE use_website_helpdesk_form = true
                 ON CONFLICT DO NOTHING
        """
    )

    whitelist_fields = [
        "partner_name",
        "partner_email",
        "name",
        "description",
        "team_id",
        "partner_id",
    ]

    cr.execute(
        """
            UPDATE ir_model_fields
                SET website_form_blacklisted = false
                WHERE model = 'helpdesk.team'
                AND name IN %s
        """,
        (tuple(whitelist_fields),),
    )
