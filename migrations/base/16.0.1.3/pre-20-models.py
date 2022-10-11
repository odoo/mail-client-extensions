# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):
    util.remove_model(cr, "base.update.translations")

    util.remove_field(cr, "ir.module.module.dependency", "write_date")
    util.remove_field(cr, "ir.module.module.dependency", "create_date")
    util.remove_field(cr, "ir.module.module.dependency", "write_uid")
    util.remove_field(cr, "ir.module.module.dependency", "create_uid")

    # moving the field company_registry from res_company to res_partner
    util.create_column(cr, "res_partner", "company_registry", "varchar")
    query = """
        UPDATE res_partner p
           SET company_registry = res_company.company_registry
          FROM res_company
         WHERE res_company.partner_id = p.id
    """
    cr.execute(query)
    util.remove_column(cr, "res_company", "company_registry")
