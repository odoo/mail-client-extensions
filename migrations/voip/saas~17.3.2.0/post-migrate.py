from odoo.upgrade import util


def migrate(cr, version):
    cr.execute("DELETE FROM ir_config_parameter WHERE key='voip.mode' RETURNING value")
    [mode] = cr.fetchone() or ["demo"]
    cr.execute("DELETE FROM ir_config_parameter WHERE key='voip.wsServer' RETURNING value")
    [ws_server] = cr.fetchone() or [None]
    cr.execute("DELETE FROM ir_config_parameter WHERE key='voip.pbx_ip' RETURNING value")
    [pbx_ip] = cr.fetchone() or [None]
    if mode or ws_server or pbx_ip:
        voip_provider_id = util.ref(cr, "voip.default_voip_provider")
        cr.execute(
            """
                UPDATE voip_provider
                   SET name = %s, mode = %s, ws_server = %s, pbx_ip = %s
                 WHERE id = %s
            """,
            ("Default", mode, ws_server, pbx_ip, voip_provider_id),
        )

        query = cr.mogrify(
            """
                UPDATE res_users_settings
                   SET voip_provider_id = %s
                 WHERE (voip_username IS NOT NULL
                    OR voip_secret IS NOT NULL)
                   AND {parallel_filter}
            """,
            [voip_provider_id],
        ).decode()
        util.explode_execute(cr, query, table="res_users_settings")
