# -*- coding: utf-8 -*-
import logging

from lxml import etree

from openerp.modules.module import get_resource_path

from openerp.addons.base.maintenance.migrations import util

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    util.create_column(cr, "payment_acquirer", "module_id", "int4")
    util.create_column(cr, "payment_acquirer", "description", "text")

    cr.execute("UPDATE payment_acquirer SET environment='test' WHERE environment != 'prod'")

    case_query = ""
    case_params = []

    files = ["payment_acquirer_data.xml", "payment_acquirer.xml"]
    for f in files:
        file_path = get_resource_path("payment", "data", f)  # return False if not found
        if file_path:
            with open(file_path) as fp:
                tree = etree.parse(fp)
                for node in tree.xpath('//field[@name="description"]'):
                    xid = node.getparent().get("id")
                    acq = xid[len("payment_acquirer_") :]

                    util.rename_xmlid(cr, "payment_{0}.{1}".format(acq, xid), "payment.{0}".format(xid))

                    desc = "".join(map(etree.tostring, node.iterchildren()))
                    case_query += "WHEN provider=%s THEN %s "
                    case_params.extend([acq, desc])

    if not case_params:  # file not found
        _logger.warning("Cannot find file: %s" % " or ".join(files))

    cr.execute(
        """
        UPDATE payment_acquirer
           SET description = CASE {0} ELSE NULL END
    """.format(
            case_query
        ),
        case_params,
    )

    cr.execute(
        """
        UPDATE payment_acquirer a
           SET module_id = m.id
          FROM ir_module_module m
         WHERE m.name = 'payment_' || a.provider
    """
    )
