# -*- coding: utf-8 -*-
from odoo.addons.base.maintenance.migrations import util

def migrate(cr, version):
    types = ['fleet.type_service_service_%d' % i for i in range(1, 19)]
    types += ['fleet.type_service_%d' % i for i in range(1, 53)]
    types += ['fleet.type_contract_%s' % x for x in 'omnium leasing repairing refueling'.split()]
    util.delete_unused(cr, 'fleet_service_type', types)

    tags = 'junior senior leasing purchased compact sedan convertible break'
    util.delete_unused(cr, 'fleet_vehicle_tag', ['fleet.vehicle_tag_%s' % t for t in tags.split()])

    models = 'corsa astra agila combotour meriva astragtc zafira zafiratourer insignia mokka antara ampera ' \
             'a1 a3 a4 a5 a6 a7 a8 q3 q5 q7 tt ' \
             'serie1 serie3 serie5 serie6 serie7 seriex seriez4 seriem seriehybrid ' \
             'classa classb classc classcl classcls classe classm classgl classglk classr classs classslk classsls'
    util.delete_unused(cr, 'fleet_vehicle_model', ['fleet.model_%s' % x for x in models.split()])
