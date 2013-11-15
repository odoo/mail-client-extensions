# -*- coding: utf-8 -*-
def migrate(cr, version):
    """In saas-2, the idea.idea wkf has been revamped completely.
       It is necessary to drop existing workitems so that the obsolete activities
       can be deleted, and then recreate appropriate instances as a post-migration
       action"""

    cr.execute("""DELETE from wkf_workitem w
                   USING wkf_instance i WHERE w.inst_id = i.id
                                          AND i.res_type=%s
               """, ('idea.idea',))
