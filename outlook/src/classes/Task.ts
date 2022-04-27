export default class Task {
    id: number;
    name: string;
    projectName: string;
    companyId: number;

    static fromJSON(o: Object): Task {
        const task = new Task();
        task.id = o['task_id'];
        task.name = o['name'];
        task.projectName = o['project_name'] || '';
        task.companyId = o['company_id'];
        return task;
    }
}
