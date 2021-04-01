# -*- coding: utf-8 -*-
from contextlib import closing

from lxml import etree
from psycopg2.extras import execute_values

from odoo.tools import file_open

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_record(cr, "base.act_view_currency_rates")

    util.create_column(cr, "res_currency", "full_name", "varchar")

    util.rename_xmlid(cr, "base.SOD", "base.SOS")
    util.rename_xmlid(cr, "base.rateSOD", "base.rateSOS")
    cr.execute("UPDATE res_currency SET name='SOS' WHERE name='SOD'")

    with closing(file_open("addons/base/data/res_currency_data.xml")) as fp:
        tree = etree.parse(fp)
        to_update_values = []
        for node in tree.xpath('//field[@name="full_name"]'):
            to_update_values += [(node.getparent().get("id"), node.text)]
        if to_update_values:
            execute_values(
                cr._obj,
                """
                WITH to_update (name, full_name) AS (VALUES %s)
                UPDATE res_currency
                   SET full_name = to_update.full_name
                  FROM to_update
                 WHERE res_currency.name = to_update.name
            """,
                to_update_values,
            )
