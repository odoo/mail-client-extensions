import { postJsonRpc } from "../utils/http";
import { URLS } from "../const";
import { getAccessToken } from "src/services/odoo_auth";

/**
 * Represent a "project.task" record.
 */
export class Task {
    id: number;
    name: string;
    projectName: string;

    /**
     * Unserialize the task object (reverse JSON.stringify).
     */
    static fromJson(values: any): Task {
        const task = new Task();
        task.id = values.id;
        task.name = values.name;
        task.projectName = values.projectName;
        return task;
    }

    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    static fromOdooResponse(values: any): Task {
        const task = new Task();
        task.id = values.task_id;
        task.name = values.name;
        task.projectName = values.project_name;
        return task;
    }

    /**
     * Make a RPC call to the Odoo database to create a task
     * and return the ID of the newly created record.
     */
    static createTask(partnerId: number, projectId: number, emailBody: string, emailSubject: string): Task {
        const url = PropertiesService.getUserProperties().getProperty("ODOO_SERVER_URL") + URLS.CREATE_TASK;
        const odooAccessToken = getAccessToken();

        const response = postJsonRpc(
            url,
            { email_subject: emailSubject, email_body: emailBody, project_id: projectId, partner_id: partnerId },
            { Authorization: "Bearer " + odooAccessToken },
        );

        const taskId = response ? response.task_id || null : null;

        if (!taskId) {
            return null;
        }

        return Task.fromJson({
            id: taskId,
            name: response.name,
        });
    }
}
