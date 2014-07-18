# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("""INSERT INTO ir_config_parameter_groups_rel(icp_id, group_id)
                       SELECT icp.id, imd.res_id
                         FROM ir_config_parameter icp, ir_model_data imd
                        WHERE icp.key = %s
                          AND imd.model = 'res.groups'
                          AND CONCAT(imd.module, '.', imd.name) IN %s
                          AND NOT EXISTS(SELECT 1
                                           FROM ir_config_parameter_groups_rel r
                                          WHERE r.icp_id = icp.id
                                            AND r.group_id = imd.res_id)
               """, ('Gengo.UUID', ('base.group_website_designer', 'base.group_website_publisher',)))
