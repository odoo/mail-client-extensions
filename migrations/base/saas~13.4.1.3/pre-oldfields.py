from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("UPDATE ir_model_data SET create_date = date_init WHERE create_date IS NULL AND date_init IS NOT NULL")
    cr.execute("UPDATE ir_model_data SET write_date = date_update WHERE write_date IS NULL AND date_update IS NOT NULL")

    cr.execute(
        """
            ALTER TABLE ir_model_data
            ALTER COLUMN create_date SET DEFAULT (now() at time zone 'UTC'),
            ALTER COLUMN  write_date SET DEFAULT (now() at time zone 'UTC')
        """
    )

    util.remove_field(cr, "ir.model.data", "date_init")
    util.remove_field(cr, "ir.model.data", "date_update")
