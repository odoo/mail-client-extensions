# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    cr.execute(
        """
            UPDATE hr_contract AS contract
               SET contract_type_id = contract_type.id
              FROM hr_contract_type AS contract_type
             WHERE contract.contract_type = contract_type.name
         """
    )
    util.remove_column(cr, "hr_contract", "contract_type")
