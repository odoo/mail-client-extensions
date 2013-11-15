# -*- coding: utf-8 -*-
def migrate(cr, version):
    """In saas-2, the idea.idea wkf has been revamped completely.
       It is necessary to recreate new workitems after dropping the
       obsolete ones in pre-migration, and re-set the instances to active.
    """
    cr.execute("""INSERT INTO wkf_workitem (inst_id, act_id, state)
                      SELECT i.id,
                             (SELECT res_id FROM ir_model_data WHERE module=%s and name=%s),
                             'completed'
                      FROM wkf_instance i WHERE i.res_type=%s
               """, ('idea', 'act_normal', 'idea.idea',))
    cr.execute("""UPDATE wkf_instance set state=%s WHERE res_type=%s""", ('active', 'idea.idea',))
