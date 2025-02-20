def migrate(cr, version):
    cr.execute("DROP INDEX IF EXISTS ir_filters_name_model_uid_unique_action_index")
