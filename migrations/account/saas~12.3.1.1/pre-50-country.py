# -*- coding: utf-8 -*-


def migrate(cr, version):
    cr.execute(
        """
        WITH cnoc AS (
         SELECT p.id AS pid,
                (regexp_matches(d.module, 'l10n_(..)(?:_|$)'))[1] AS cc
           FROM res_company c
           JOIN res_partner p ON p.id = c.partner_id
           JOIN ir_model_data d ON (d.model = 'account.chart.template' AND d.res_id = c.chart_template_id)
          WHERE p.country_id IS NULL
        )
        , upd AS (
         SELECT n.pid, c.id AS cid
           FROM cnoc n
           JOIN res_country c ON (lower(c.code) = lower(n.cc))
        )
         UPDATE res_partner p
            SET country_id = upd.cid
           FROM upd
          WHERE upd.pid = p.id
        """
    )
