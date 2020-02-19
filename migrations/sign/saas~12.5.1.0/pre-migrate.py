# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    util.create_column(cr, "sign_request_item", "sms_number", "varchar")
    util.create_column(cr, "sign_request_item", "signer_email", "varchar")
    util.create_column(cr, "sign_request_item", "access_via_link", "boolean")
    util.create_column(cr, "sign_template", "redirect_url_text", "varchar")

    cr.execute(
        """
        UPDATE sign_request_item s
           SET sms_number=p.mobile,
               signer_email=p.email
          FROM res_partner p
         WHERE p.id=s.partner_id
        """
    )
    cr.execute("UPDATE sign_template SET redirect_url_text='Open Link'")
    cr.execute("DELETE FROM sign_send_request_signer")

    util.remove_field(cr, "sign.template", "extension")
    util.remove_field(cr, "sign.send.request", "extension")
    util.rename_model(cr, "sign.item.value", "sign.request.item.value")
    util.create_column(cr, "sign_request_item_value", "sign_request_item_id", "int4")

    cr.execute(
        """
    with vv as (SELECT v.id vid ,r.id rid
                  FROM sign_request_item_value v
                  JOIN sign_item i ON v.sign_item_id=i.id
             LEFT JOIN sign_request_item r ON v.sign_request_id=r.sign_request_id AND r.role_id=i.responsible_id),

     nullvid as (SELECT vv.vid
                   FROM vv
                  WHERE rid is null),

     vv2 as (SELECT v.id vid ,r.id rid
               FROM sign_request_item_value v
               JOIN sign_item i ON v.sign_item_id=i.id
          LEFT JOIN sign_request_item r ON v.sign_request_id=r.sign_request_id AND v.id IN (SELECT vid FROM nullvid)),

    allvv as (SELECT vid,rid
                FROM vv where rid IS NOT NULL
        UNION ALL
              SELECT vid,rid
                FROM vv2
               WHERE rid IS NOT NULL)

    UPDATE sign_request_item_value v
       SET sign_request_item_id=allvv.rid
      FROM allvv
     WHERE allvv.vid=v.id
    """
    )
