try:
    from odoo.addons.iap.tools.iap_tools import iap_jsonrpc
except ImportError:
    from odoo.addons.iap import jsonrpc as iap_jsonrpc

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    cr.execute("DELETE FROM ir_config_parameter WHERE key LIKE 'mail_push.fcm_%'")
    cr.execute("DELETE FROM ir_config_parameter WHERE key='mail_push.mail_push_notification' RETURNING value")
    [value] = cr.fetchone() or ["False"]
    if util.str2bool(value, default=False):
        RCS = util.env(cr)["res.config.settings"]
        RCS.create({"ocn_push_notification": True}).execute()

        endpoint = RCS._get_endpoint()
        ocnuuid = RCS._get_ocn_uuid()

        # re-register devices
        def iap(pid, pname, device, subscription):
            params = {
                "ocn_uuid": ocnuuid,
                "user_name": pname,
                "user_login": str(pid),
                "device_name": device,
                "device_key": subscription,
            }
            return iap_jsonrpc(endpoint + "/iap/ocn/register_device", params=params)

        cr.execute("""
            SELECT p.id, p.name,
                   d.name, d.subscription_id
              FROM mail_push_device d
              JOIN res_partner p ON p.id = d.partner_id
             WHERE d.service_type = 'fcm'
                AND d.subscription_id IS NOT NULL
          ORDER BY d.id
        """)
        for pid, pname, device, subscription_id in cr.fetchall():
            token = iap(pid, pname, device, subscription_id)
            if token:
                cr.execute("UPDATE res_partner SET ocn_token = %s WHERE id = %s", [token, pid])

    # odoo/enterprise@7587be4663c39f6388d752c0eb5f81f53a1ba9f8
    util.remove_field(cr, "res.partner", "device_identity_ids")
    util.remove_field(cr, "res.users", "device_identity_ids", drop_column=False)
    util.remove_model(cr, "mail_push.device")
