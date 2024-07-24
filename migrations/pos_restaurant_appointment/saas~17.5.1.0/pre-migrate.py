from odoo.upgrade import util


def migrate(cr, version):
    util.create_column(cr, "pos_config", "appointment_type_id", "int4")
    cr.execute(
        """
        WITH subquery AS (
            SELECT pos_config_id,
                   MIN(appointment_type_id) AS first_appointment_type_id
              FROM appointment_type_pos_config_rel
             GROUP BY pos_config_id
        )
        UPDATE pos_config pc
           SET appointment_type_id = subquery.first_appointment_type_id
          FROM subquery
         WHERE pc.id = subquery.pos_config_id;
        """
    )

    util.rename_field(cr, "res.config.settings", "pos_appointment_type_ids", "pos_appointment_type_id")
    util.rename_field(cr, "pos.config", "appointment_type_ids", "appointment_type_id")

    cr.execute("DROP TABLE appointment_type_pos_config_rel")
