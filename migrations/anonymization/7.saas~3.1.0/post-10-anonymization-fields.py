from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
        data = [

            (1, 'sql', 'name', 'res.partner',
              "update res_partner set name = coalesce(%(value)s, '') where id = %(id)s"),

            (1, 'sql', 'email', 'res.partner',
              "update res_partner set email = coalesce(%(value)s, '') where id = %(id)s"),

            (1, 'sql', 'phone', 'res.partner',
              "update res_partner set phone = coalesce(%(value)s, '') where id = %(id)s"),

            (2, 'sql', 'name', 'res.partner',
             "update res_company set name = coalesce(%(value)s, '') where partner_id = %(id)s"),

            (2, 'sql', 'email', 'res.partner',
             "update res_company set email = coalesce(%(value)s, '') where partner_id = %(id)s"),

            (2, 'sql', 'phone', 'res.partner',
             "update res_company set phone = coalesce(%(value)s, '') where partner_id = %(id)s"),

        ]

        sql_insert = """INSERT INTO ir_model_fields_anonymization_migration_fix (
                            target_version, sequence, query_type, field_name, model_name, query
                        ) VALUES (
                            '8.0', %s, %s, %s, %s, %s)"""

        for line in data:
            cr.execute(sql_insert, line)

