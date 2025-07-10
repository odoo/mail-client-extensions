from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("""
        CREATE TABLE ir_actions_server_history (
            id SERIAL NOT NULL PRIMARY KEY,
            action_id INTEGER,
            code TEXT,
            create_uid INTEGER,
            write_uid INTEGER,
            create_date TIMESTAMP WITHOUT TIME ZONE,
            write_date TIMESTAMP WITHOUT TIME ZONE
        )
    """)
    cr.execute("""
        INSERT INTO ir_actions_server_history (
                        action_id,
                        code,
                        create_uid,
                        create_date,
                        write_uid,
                        write_date
                    )
             SELECT a.id,
                    a.code,
                    a.write_uid,
                    a.write_date,
                    a.write_uid,
                    a.write_date
               FROM ir_act_server a
              WHERE a.state = 'code'
    """)

    util.remove_field(cr, "ir.model.fields", "complete_name")
    cr.execute("DROP INDEX IF EXISTS ir_model_constraint__type_index")

    util.remove_field(cr, "res.lang", "short_time_format")
    util.remove_field(cr, "res.lang", "short_date_format")
