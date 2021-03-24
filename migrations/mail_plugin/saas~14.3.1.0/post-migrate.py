# -*- coding: utf-8 -*-

from odoo.addons.iap.tools import iap_tools

from odoo.upgrade import util


def migrate(cr, version):
    cr.execute(
        """
       INSERT INTO res_partner_iap (partner_id, iap_search_domain, iap_enrich_info)
            SELECT id,
                   -- entire email if the domain is blacklisted
                   -- otherwise just the domain
                   CASE
                       WHEN SPLIT_PART(email, '@', 2) = ANY(%s)
                       THEN email
                       ELSE SPLIT_PART(email, '@', 2)
                   END,
                   iap_enrich_info
              FROM res_partner
             WHERE iap_enrich_info IS NOT NULL
               AND is_company IS TRUE
               AND email LIKE '%%@%%'
        """,
        [list(iap_tools._MAIL_DOMAIN_BLACKLIST)],
    )

    util.remove_column(cr, "res_partner", "iap_enrich_info")
