import { User } from "../models/user";

export function getOdooRecordURL(user: User, model: string, record_id: number) {
    return user.odooUrl + `/mail_plugin/redirect_to_record/${model}/?record_id=${record_id}`;
}
