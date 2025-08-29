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
                       'data_merge_field_crm_lead_email_from',
                       'data_merge_field_crm_lead_partner_name',
                       'data_merge_field_crm_lead_contact_name',
                       'data_merge_field_crm_tag_name',
                       'data_merge_field_crm_lost_reason_name'
                   )
               AND r.match_mode = 'accent'
            """
        )
