# -*- coding: utf-8 -*-
from openerp.addons.base.maintenance.migrations import util

def migrate(cr, version):
    def rename(a, b):
        util.rename_xmlid(cr, 'fleet.' + a, 'fleet.' + b)

    rename('group_fleet_user', 'fleet_group_user')
    rename('group_fleet_manager', 'fleet_group_manager')

    rules = util.splitlines("""
        contract
        cost
        service
        odometer
        fuel_log
        vehicule
    """)
    for r in rules:
        rename('fleet_user_{0}_visibility'.format(r),
               'fleet_rule_{0}_visibility_user'.format(r))
        rename('fleet_user_{0}_visibility_manager'.format(r),
               'fleet_rule_{0}_visibility_manager'.format(r))

    renames = util.splitlines("""
        # groups
        group_fleet_user    fleet_group_user
        group_fleet_manager fleet_group_manager

        # reporting actions
        action_fleet_reporting_costs        fleet_costs_reporting_action
        action_view_fleet_reporting_pivot   fleet_reporting_pivot_action
        action_view_fleet_reporting_graph   fleet_reporting_graph_action
        action_fleet_reporting_costs_non_effective  fleet_costs_reporting_non_effective_action
        action_view_fleet_non_effective_pivot       view_fleet_non_effective_pivot_action
        action_view_fleet_non_effective_graph       view_fleet_non_effective_graph_action

        # reporting views
        fleet_vehicle_effective_costs_report_pivot  fleet_vehicle_cost_view_pivot
        fleet_vehicle_effective_costs_report        fleet_vehicle_cost_view_graph
        fleet_vehicle_indicative_costs_report_pivot fleet_vehicle_cost_indicative_view_pivot
        fleet_vehicle_indicative_costs_report       fleet_vehicle_cost_indicative_view_graph
    """)
    for r in renames:
        rename(*r.split())

    models = util.splitlines("""
        vehicle_model
        vehicle_model_brand
        vehicle_state
        vehicle
        vehicle_log_contract
        vehicle_odometer
        vehicle_log_fuel
        vehicle_log_services
        vehicle_tag_view           # was already named correctly :p
        vehicle_service_types
        vehicle_costs
    """)
    for m in models:
        # not all models have all view types, but it does matter.
        for v in 'form tree search kanban graph pivot'.split():
            rename('fleet_{0}_{1}'.format(m, v), 'fleet_{0}_view_{1}'.format(m, v))
        rename('fleet_{0}_act'.format(m), 'fleet_{0}_action'.format(m))
