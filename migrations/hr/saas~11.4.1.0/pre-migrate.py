# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util


def migrate(cr, version):
    moves = {
        "hr_contract": {"place_of_birth", "children", "vehicle_distance"},
        "hr_contract_salary": {
            "additional_note",
            "certificate",
            "study_field",
            "study_school",
            "emergency_contact",
            "emergency_phone",
        },
    }

    for module, fields in moves.items():
        for field in fields:
            util.move_field_to_module(cr, "hr.employee", field, module, "hr")

    util.rename_field(cr, "hr.employee", "vehicle_distance", "km_home_work")

    util.create_column(cr, "hr_employee", "certificate", "varchar")  # force empty if not already present
