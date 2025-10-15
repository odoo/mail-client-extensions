import { getOdooServerUrl } from "./app_properties";

export function getOdooRecordURL(model, record_id) {
    return getOdooServerUrl() + `/mail_plugin/redirect_to_record/${model}/?record_id=${record_id}`;
}
