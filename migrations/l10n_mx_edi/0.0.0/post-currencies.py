# -*- coding: utf-8 -*-
from contextlib import closing

from lxml import etree

from odoo.tools import file_open

from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    if util.version_gte("saas~11.3"):
        _force_decimal_places(cr)


def _force_decimal_places(cr):
    # currencies being in `noupdate`, force loading of `l10n_mx_edi_decimal_places` data
    places = []
    with closing(file_open("addons/l10n_mx_edi/data/res_currency_data.xml")) as fp:
        tree = etree.parse(fp)
        for node in tree.xpath('//record[@model="res.currency"]/field[@name="l10n_mx_edi_decimal_places"]'):
            _, _, name = node.getparent().get("id").partition(".")
            places.append((int(node.text), name))

    cr.executemany(
        """
        UPDATE res_currency
           SET l10n_mx_edi_decimal_places=%s
         WHERE id = (SELECT res_id
                       FROM ir_model_data
                      WHERE model='res.currency'
                        AND module='base'
                        AND name=%s)
    """,
        places,
    )
