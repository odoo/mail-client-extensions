import logging

from odoo.upgrade import util


def migrate(cr, version):
    _logger = logging.getLogger(__name__)

    cr.execute(r"SELECT model,name FROM ir_model_fields WHERE state='manual' AND name like 'x\_% %'")
    for model, name in cr.fetchall():
        new_name = name.strip().replace(" ", "_")
        util.rename_field(cr, model, name, new_name)
        _logger.info("ir_model_data_name_nospaces: '%s' renamed field '%s' to '%s'", model, name, new_name)
