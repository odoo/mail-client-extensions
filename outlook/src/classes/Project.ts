export default class Project {
    id: number;
    name: string;

    static fromJson(projectJson: Object): Project {
        const project = new Project();
        project.id = projectJson['id'];
        project.name = projectJson['name'];
        return project;
    }
}
