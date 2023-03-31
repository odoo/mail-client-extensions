/**
 * Represent a "project.project" record.
 */
var Project = /** @class */ (function () {
    function Project() {}
    /**
     * Unserialize the project object (reverse JSON.stringify).
     */
    Project.fromJson = function (values) {
        var project = new Project();
        project.id = values.id;
        project.name = values.name;
        project.partnerName = values.partnerName;
        return project;
    };
    /**
     * Parse the dictionary return by the Odoo endpoint.
     */
    Project.fromOdooResponse = function (values) {
        var project = new Project();
        project.id = values.project_id;
        project.name = values.name;
        project.partnerName = values.partner_name;
        return project;
    };
    /**
     * Make a RPC call to the Odoo database to search a project.
     */
    Project.searchProject = function (query) {
        var url = State.odooServerUrl + URLS.SEARCH_PROJECT;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(url, { search_term: query }, { Authorization: "Bearer " + accessToken });
        if (!response) {
            return [[], new ErrorMessage("http_error_odoo")];
        }
        return [
            response.map(function (values) {
                return Project.fromOdooResponse(values);
            }),
            new ErrorMessage(),
        ];
    };
    /**
     * Make a RPC call to the Odoo database to create a project
     * and return the newly created record.
     */
    Project.createProject = function (name) {
        var url = State.odooServerUrl + URLS.CREATE_PROJECT;
        var accessToken = State.accessToken;
        var response = (0, postJsonRpc)(url, { name: name }, { Authorization: "Bearer " + accessToken });
        var projectId = response ? response.project_id || null : null;
        if (!projectId) {
            return null;
        }
        return Project.fromJson({
            id: projectId,
            name: response.name,
        });
    };
    return Project;
})();
