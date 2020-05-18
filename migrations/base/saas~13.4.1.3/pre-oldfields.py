from odoo.upgrade import util

def migrate(cr, version):
    cr.execute("""
        UPDATE ir_model_data
        SET create_date = coalesce(create_date, date_init),
             write_date = coalesce(write_date, date_update)
    """)
    cr.execute("""
        ALTER TABLE ir_model_data
        ALTER COLUMN create_date SET DEFAULT (now() at time zone 'UTC'),
        ALTER COLUMN  write_date SET DEFAULT (now() at time zone 'UTC')
    """)
