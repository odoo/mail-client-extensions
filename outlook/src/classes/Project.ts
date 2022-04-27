export default class Project {
    id: number;
    name: string;
    company_id: number;

    static fromJson(projectJson: Object): Project {
        const project = new Project();
        project.id = projectJson['project_id'];
        project.name = projectJson['name'];
        project.company_id = projectJson['company_id'];
        return project;
    }
}
