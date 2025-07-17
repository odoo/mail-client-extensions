import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { getAccessToken } from "src/services/odoo_auth";
import { _t } from "../services/translation";

/**
 * Represent a "mail.activity" record.
 */
export class Activity {
    id: number;
    summary: string;
    dateDeadlineStr: string;
    dateDeadlineTimestamp: number;
    resId: string;
    resModel: string;
    resName: string;

    /**
     * Unserialize the activity object (reverse JSON.stringify).
     */
    static fromJson(values: any): Activity {
        const activity = new Activity();
        activity.id = values.id;
        activity.summary = values.summary;
        activity.dateDeadlineStr = values.dateDeadlineStr;
        activity.dateDeadlineTimestamp = values.dateDeadlineTimestamp;
        activity.resId = values.resId;
        activity.resModel = values.resModel;
        activity.resName = values.resName;
        return activity;
    }

    /**
     * Parse the dictionary returned by the Odoo database endpoint.
     */
    static fromOdooResponse(values: any): Activity {
        const activity = new Activity();
        activity.id = values.id;
        activity.summary = values.summary;
        activity.dateDeadlineStr = values.date_deadline_str;
        activity.dateDeadlineTimestamp = values.date_deadline_timestamp;
        activity.resId = values.res_id;
        activity.resModel = values.res_model;
        activity.resName = values.res_name;
        return activity;
    }

    static getActivities(): [string, Activity[]][] | null {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.GET_ACTIVITIES;
        const odooAccessToken = getAccessToken();
        if (!odooAccessToken || !odooAccessToken) {
            return null;
        }

        const response = postJsonRpc(url, {}, { Authorization: "Bearer " + odooAccessToken });
        if (!response) {
            return null;
        }

        return response.map((values: any) => [
            values[0],
            values[1].map((v) => Activity.fromOdooResponse(v)),
        ]);
    }

    /**
     * Make a RPC call to the Odoo database to mark as done the activity.
     */
    markDone(): boolean {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.DONE_ACTIVITY;
        const accessToken = getAccessToken();
        const response = postJsonRpc(
            url,
            { activity_id: this.id },
            { Authorization: "Bearer " + accessToken },
        );
        return response?.ok || false;
    }

    /**
     * Make a RPC call to the Odoo database to cancel the activity.
     */
    markCancel(): boolean {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.CANCEL_ACTIVITY;
        const accessToken = getAccessToken();
        const response = postJsonRpc(
            url,
            { activity_id: this.id },
            { Authorization: "Bearer " + accessToken },
        );
        return response?.ok || false;
    }

    /**
     * Make a RPC call to the Odoo database to edit the activity.
     * Return the new state of the activities.
     */
    edit(summary: string, dateDeadlineTimestamp: number): [string, Activity[]][] | null {
        const url =
            PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") +
            URLS.EDIT_ACTIVITY;
        const accessToken = getAccessToken();
        const response = postJsonRpc(
            url,
            {
                activity_id: this.id,
                summary,
                date_deadline_timestamp: Math.floor(dateDeadlineTimestamp / 1000),
            },
            { Authorization: "Bearer " + accessToken },
        );
        if (!response) {
            return null;
        }
        return response.map((values: any) => [
            values[0],
            values[1].map((v) => Activity.fromOdooResponse(v)),
        ]);
    }
}
