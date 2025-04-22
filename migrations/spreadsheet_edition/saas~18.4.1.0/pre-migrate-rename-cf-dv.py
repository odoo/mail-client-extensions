from odoo.upgrade.util.spreadsheet import iter_commands

data_validation_rule_conversion_map = {
    "textContains": "containsText",
    "textNotContains": "notContainsText",
    "textIs": "isEqualText",
    "textIsEmail": "isEmail",
    "textIsLink": "isLink",
}

conditional_format_operator_conversion_map = {
    "BeginsWith": "beginsWithText",
    "Between": "isBetween",
    "ContainsText": "containsText",
    "EndsWith": "endsWithText",
    "Equal": "isEqual",
    "GreaterThan": "isGreaterThan",
    "GreaterThanOrEqual": "isGreaterOrEqualTo",
    "IsEmpty": "isEmpty",
    "IsNotEmpty": "isNotEmpty",
    "LessThan": "isLessThan",
    "LessThanOrEqual": "isLessOrEqualTo",
    "NotBetween": "isNotBetween",
    "NotContains": "notContainsText",
    "NotEqual": "isNotEqual",
}


def migrate(cr, version):
    for commands in iter_commands(cr, like_any=[r"%ADD\_CONDITIONAL\_FORMAT%", r"%ADD\_DATA\_VALIDATION\_RULE%"]):
        for cmd in commands:
            if cmd["type"] == "ADD_DATA_VALIDATION_RULE":
                rule_type = cmd["rule"]["criterion"]["type"]
                converted_type = data_validation_rule_conversion_map.get(rule_type)
                if converted_type:
                    cmd["rule"]["criterion"]["type"] = converted_type
            elif cmd["type"] == "ADD_CONDITIONAL_FORMAT" and cmd["cf"]["rule"]["type"] == "CellIsRule":
                operator = cmd["cf"]["rule"]["operator"]
                converted_operator = conditional_format_operator_conversion_map.get(operator)
                if converted_operator:
                    cmd["cf"]["rule"]["operator"] = converted_operator
