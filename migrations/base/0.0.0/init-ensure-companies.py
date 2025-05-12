import os


def prepare_migration(cr):
    source = os.getenv("ODOO_UPG_DB_SOURCE_VERSION", "")
    target = os.getenv("ODOO_UPG_DB_TARGET_VERSION")
    if source.startswith(("15.0", "16.0", "17.0", "saas~17", "18.0")) and target != "16.0":
        cr.execute(
            """
            INSERT INTO res_company_users_rel(cid, user_id)
                 SELECT c.id, imd.res_id
                   FROM res_company c,
                        ir_model_data imd
                  WHERE imd.name = 'user_root'
                    AND imd.module = 'base'
            ON CONFLICT DO NOTHING
            """
        )
