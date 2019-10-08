# -*- coding: utf-8 -*-
from ast import literal_eval
import logging
from odoo.addons.base.maintenance.migrations import util


_logger = logging.getLogger("odoo.addons.base.maintenance.migrations.base.saas~12-2." + __name__)


def migrate(cr, version):
    cr.execute(
        """
        SELECT id, model, quote_ident(name), selection
          FROM ir_model_fields
         WHERE state = 'manual'
           AND ttype = 'selection'
           AND store = TRUE
    """
    )
    for fid, model, column, selection in cr.fetchall():
        selection = literal_eval(selection.strip())
        if not any(isinstance(k, int) for k, l in selection):
            continue
        _logger.info("convert field %s:%s to str-selection", model, column)
        selection = repr([(str(k), l) for k, l in selection])
        table = util.table_of_model(cr, model)
        cr.execute("ALTER TABLE {} ALTER COLUMN {} TYPE VARCHAR".format(table, column))
        cr.execute("UPDATE ir_model_fields SET selection = %s WHERE id = %s", [selection, fid])
