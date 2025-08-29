from odoo.modules.db import has_unaccent


def migrate(cr, version):
    if not has_unaccent(cr):
        cr.execute(
            """
            UPDATE data_merge_rule r
               SET match_mode = 'exact'
              FROM ir_model_data d
             WHERE r.id = d.res_id
               AND d.module = 'data_merge'
               AND d.name IN (
                    'data_merge_field_res_partner_name',
                    'data_merge_field_res_partner_email',
                    'data_merge_field_res_partner_category_name',
                    'data_merge_field_res_partner_industry_name',
                    'data_merge_field_res_partner_industry_full_name',
                    'data_merge_field_res_country_name',
                    'data_merge_field_res_country_state'
                   )
               AND r.match_mode = 'accent'
            """
        )
