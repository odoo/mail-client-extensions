from odoo.modules.db import has_unaccent


def migrate(cr, version):
    if not has_unaccent(cr):
        cr.execute(
            """
            UPDATE data_merge_rule r
               SET match_mode = 'exact'
              FROM ir_model_data d
             WHERE r.id = d.res_id
               AND d.module = 'data_merge_crm'
               AND d.name IN (
                    'data_merge_field_utm_campaign_name',
                    'data_merge_field_utm_medium_name',
                    'data_merge_field_utm_source_name'
                   )
               AND r.match_mode = 'accent'
            """
        )
