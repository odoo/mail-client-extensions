from odoo.upgrade.util.spreadsheet import iter_commands


def migrate(cr, version):
    for commands in iter_commands(
        cr,
        like_any=[
            r"%UPDATE\_CHART%",
            r"%SELECT\_FIGURE%",
            r"%CREATE\_FIGURE%",
            r"%UPDATE\_FIGURE%",
            r"%DELETE\_FIGURE%",
            r"%CREATE\_IMAGE%",
            r"%CREATE\_CHART%",
        ],
    ):
        for command in commands:
            cmdType = command["type"]
            if cmdType == "CREATE_IMAGE":
                migrate_position(command)
            elif cmdType == "CREATE_CHART":
                migrate_id(command)
                migrate_position(command)
            elif cmdType == "UPDATE_FIGURE":
                migrate_id(command)
                migrate_x_y(command)
            elif cmdType == "CREATE_FIGURE":
                migrate_figure_object(command)
            elif cmdType in [
                "DELETE_FIGURE",
                "UPDATE_CHART",
                "SELECT_FIGURE",
            ]:
                migrate_id(command)


def migrate_id(cmd):
    cmd["figureId"] = cmd["id"]
    del cmd["id"]


def migrate_position(cmd):
    if "position" in cmd:
        cmd["offset"] = cmd["position"]
        cmd["col"] = 0
        cmd["row"] = 0
        del cmd["position"]
    else:
        cmd["offset"] = {"x": 0, "y": 0}
        cmd["col"] = 0
        cmd["row"] = 0


def migrate_x_y(cmd):
    offset = {}
    for dim in ["x", "y"]:
        if dim in cmd:
            offset[dim] = cmd[dim]
            del cmd[dim]
    if offset:
        cmd["offset"] = offset


def migrate_figure_object(cmd):
    cmd["col"] = 0
    cmd["row"] = 0
    offset = {}
    for key, value in cmd["figure"].items():
        if key == "id":
            cmd["figureId"] = value
        elif key in ["x", "y"]:
            offset[key] = value
        else:
            cmd[key] = value
    cmd["offset"] = offset
    del cmd["figure"]
