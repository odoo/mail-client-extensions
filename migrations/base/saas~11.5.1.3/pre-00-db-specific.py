# -*- coding: utf-8 -*-
import logging
from odoo.addons.base.maintenance.migrations import util

NS = "odoo.addons.base.maintenance.migrations.base.saas~11.5"
_logger = logging.getLogger(NS + __name__)


def _db_openerp(cr, version):

    # some cleanups
    # VZ -> VER (Veracruz)
    util.replace_record_references(cr, ("res.country.state", 133), ("res.country.state", 974))
    util.remove_record(cr, ("res.country.state", 133))

    cr.execute(
        """
        UPDATE openerp_enterprise_database_app
           SET name = 'account',
               module_id = (SELECT id FROM ir_module_module WHERE name='account')
         WHERE module_id = (SELECT id FROM ir_module_module WHERE name='account_invoicing')
    """
    )
    cr.execute(
        """
        DELETE FROM openerp_enterprise_database_app
              WHERE module_id = (SELECT id FROM ir_module_module WHERE name='website_forum_doc')
    """
    )
    cr.execute(
        """
        DELETE FROM openerp_enterprise_database_app
              WHERE module_id = (SELECT id FROM ir_module_module WHERE name='website_version')
    """
    )

    util.remove_view(cr, "openerp_website.default_og")
    cr.execute(
        """
        UPDATE ir_attachment
           SET name='social_default_image',
               res_model='website',
               res_field='social_default_image',
               res_id=1,
               type='binary',
               url=NULL
         WHERE id=6908016
    """
    )

    util.remove_module(cr, "openerp_neopost")  # 🎉


def migrate(cr, version):
    util.dispatch_by_dbuuid(cr, version, {"8851207e-1ff9-11e0-a147-001cc0f2115e": _db_openerp})
