from odoo.upgrade import util


def migrate(cr, version):
    removed_vn_states = [
        "state_vn_VN-03",
        "state_vn_VN-06",
        "state_vn_VN-14",
        "state_vn_VN-20",
        "state_vn_VN-24",
        "state_vn_VN-27",
        "state_vn_VN-28",
        "state_vn_VN-31",
        "state_vn_VN-32",
        "state_vn_VN-36",
        "state_vn_VN-40",
        "state_vn_VN-41",
        "state_vn_VN-43",
        "state_vn_VN-46",
        "state_vn_VN-47",
        "state_vn_VN-50",
        "state_vn_VN-51",
        "state_vn_VN-52",
        "state_vn_VN-53",
        "state_vn_VN-54",
        "state_vn_VN-55",
        "state_vn_VN-57",
        "state_vn_VN-58",
        "state_vn_VN-61",
        "state_vn_VN-63",
        "state_vn_VN-67",
        "state_vn_VN-70",
        "state_vn_VN-72",
        "state_vn_VN-73",
    ]
    util.delete_unused(cr, *[f"base.{state}" for state in removed_vn_states])
