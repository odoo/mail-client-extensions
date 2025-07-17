export default class Task {
    id: number;
    name: string;
    projectName: string;

    static fromJSON(o: Object): Task {
        const task = new Task();
        task.id = o['id'];
        task.name = o['name'];
        task.projectName = o['project_name'] || '';
        return task;
    }
}
