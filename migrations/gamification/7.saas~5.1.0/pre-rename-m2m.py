# -*- coding: utf-8 -*-

def migrate(cr, version):
    cr.execute("ALTER TABLE user_ids RENAME TO gamification_challenge_users_rel")
    cr.execute("UPDATE ir_model_relation set name=%s where name=%s and model = (SELECT id FROM ir_model where model = %s)",
    	('gamification_challenge_users_rel', 'user_ids', 'gamification.challenge'))
    cr.execute("ALTER TABLE invited_user_ids RENAME TO gamification_invited_user_ids_rel")
    cr.execute("UPDATE ir_model_relation set name=%s where name=%s and model = (SELECT id FROM ir_model where model = %s)",
    	('gamification_invited_user_ids_rel', 'invited_user_ids', 'gamification.challenge'))
    cr.execute("ALTER TABLE rel_badge_badge RENAME TO gamification_badge_rule_badge_rel")
    cr.execute("UPDATE ir_model_relation set name=%s where name=%s and model = (SELECT id FROM ir_model where model = %s)",
    	('gamification_badge_rule_badge_rel', 'rel_badge_badge', 'gamification.goal.badge'))
