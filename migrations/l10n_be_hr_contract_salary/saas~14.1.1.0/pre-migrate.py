# -*- coding: utf-8 -*-

from odoo.upgrade import util


def migrate(cr, version):

    util.create_column(cr, "generate_simulation_link", "new_car", "boolean")
    util.create_column(cr, "generate_simulation_link", "car_id", "int4")
    # The contract_type selection values only have sense in Belgium (PFI, CDI, CDD),
    # that's why we have decided to create a Many2one to hr_contract_type (new model).
    # generate.simulation.link being a Transcient Model, no need to migrate the data.
    util.create_column(cr, "generate_simulation_link", "contract_type_id", "int4")
    util.remove_field(cr, "generate.simulation.link", "contract_type")
