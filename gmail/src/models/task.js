/**
 * Represent a "project.task" record.
 */
var Task = /** @class */ (function () {
    function Task() {}
    /**
     * Unserialize the task object (reverse JSON.stringify).
     */
    Task.fromJson = function (values) {
        var task = new Task();
        task.id = values.id;
        task.name = values.name;
        task.projectName = values.projectName;
        return task;
    };
    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    Task.fromOdooResponse = function (values) {
        var task = new Task();
        task.id = values.task_id;
        task.name = values.name;
        task.projectName = values.project_name;
        return task;
    };
    /**
     * Make a RPC call to the Odoo database to create a task
     * and return the ID of the newly created record.
     */
    Task.createTask = function (partnerId, projectId, emailBody, emailSubject) {
        var url = State.odooServerUrl + URLS.CREATE_TASK;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(
            url,
            { email_subject: emailSubject, email_body: emailBody, project_id: projectId, partner_id: partnerId },
            { Authorization: "Bearer " + accessToken },
        );
        var taskId = response ? response.task_id || null : null;
        if (!taskId) {
            return null;
        }
        return Task.fromJson({
            id: taskId,
            name: response.name,
        });
    };
    return Task;
})();
