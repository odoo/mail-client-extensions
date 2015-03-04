from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    cr.execute("""(SELECT display_name 
                        FROM res_partner 
                      WHERE name ilike 'xxx%' limit 1) 
                   UNION (SELECT field_name 
                        FROM ir_model_fields_anonymization 
                      WHERE field_name = 'display_name'
                   AND model_name = 'res.partner')
                """)
    anonymize_val = cr.fetchall()
    if len(anonymize_val) == 1 and 'display_name' != str(vals[0] for vals in anonymize_val):
        data = [
            (1, 'sql', 'name', 'res.partner',
             "update res_partner set name = %(value)s where id = %(id)s"),
            (2, 'sql', 'name', 'res.partner',
             "update res_partner set display_name = %(value)s where id = %(id)s"),
        ]

        sql_insert = """INSERT INTO ir_model_fields_anonymization_migration_fix (
                            target_version, sequence, query_type, field_name, model_name, query
                        ) VALUES (
                            '8.0', %s, %s, %s, %s, %s)"""

        for line in data:
            cr.execute(sql_insert, line)
