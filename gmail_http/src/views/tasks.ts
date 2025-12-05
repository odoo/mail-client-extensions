import { Project } from "../models/project";
import { State } from "../models/state";
import { User } from "../models/user";
import { logEmail } from "../services/log_email";
import { getOdooRecordURL } from "../services/odoo_redirection";
import {
    ActionCall,
    EventResponse,
    Notify,
    OpenLink,
    PushCard,
    registerEventHandler,
    UpdateCard,
} from "../utils/actions";
import {
    Button,
    Card,
    CardSection,
    DecoratedText,
    IconButton,
    LinkButton,
} from "../utils/components";
import { getCreateTaskView } from "./create_task";
import { UI_ICONS } from "./icons";
import { getPartnerView } from "./partner";
import { getSearchRecordView } from "./search_records";

async function onCreateTask(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    let noProject = false;
    if (!state.searchedProjects) {
        // Initiate the search
        const [searchedProjects, error] = await Project.searchProject(user, "");
        if (error.code) {
            return new Notify(error.message);
        }

        state.searchedProjects = searchedProjects;
        noProject = !state.searchedProjects.length;
    }
    return new PushCard(getCreateTaskView(state, _t, user, "", noProject));
}
registerEventHandler(onCreateTask);

function onSearchTasksClick(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new PushCard(
        getSearchRecordView(
            state,
            _t,
            "project.task",
            _t("Tasks"),
            _t("Log the email on the task"),
            _t("Email already logged on the task"),
            "projectName",
            "",
            true,
            state.partner.tasks,
        ),
    );
}
registerEventHandler(onSearchTasksClick);

async function onLogEmailOnTask(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): Promise<EventResponse> {
    const taskId = args.taskId;

    const error = await logEmail(_t, user, taskId, "project.task", state.email);
    if (error.code) {
        return new Notify(error.message);
    }
    state.email.setLoggingState(user, "project.task", taskId);
    return new UpdateCard(getPartnerView(state, _t, user));
}
registerEventHandler(onLogEmailOnTask);

function onEmailAlreadyLoggedOnTask(
    state: State,
    _t: Function,
    user: User,
    args: Record<string, any>,
    formInputs: Record<string, any>,
): EventResponse {
    return new Notify(_t("Email already logged on the task"));
}
registerEventHandler(onEmailAlreadyLoggedOnTask);

export function buildTasksView(state: State, _t: Function, user: User, card: Card) {
    const partner = state.partner;
    if (!partner.tasks) {
        return;
    }

    const tasks = [...partner.tasks].splice(0, 5);

    const tasksSection = new CardSection();

    const searchButton = new IconButton(
        new ActionCall(state, onSearchTasksClick),
        UI_ICONS.search,
        _t("Search Tasks"),
    );

    const title = partner.taskCount ? _t("Tasks (%s)", partner.taskCount) : _t("Tasks");
    const widget = new DecoratedText(
        "",
        "<b>" + title + "</b>",
        undefined,
        undefined,
        searchButton,
    );
    tasksSection.addWidget(widget);

    const createButton = new Button(_t("New"), new ActionCall(state, onCreateTask));
    tasksSection.addWidget(createButton);

    for (let task of tasks) {
        let taskButton = null;
        if (state.email.checkLoggingState("project.task", task.id)) {
            taskButton = new IconButton(
                new ActionCall(state, onEmailAlreadyLoggedOnTask),
                UI_ICONS.email_logged,
                _t("Email already logged on the task"),
            );
        } else {
            taskButton = new IconButton(
                new ActionCall(state, onLogEmailOnTask, {
                    taskId: task.id,
                }),
                UI_ICONS.email_in_odoo,
                _t("Log the email on the task"),
            );
        }

        tasksSection.addWidget(
            new DecoratedText(
                "",
                task.name,
                undefined,
                task.projectName,
                taskButton,
                new OpenLink(getOdooRecordURL(user, "project.task", task.id)),
            ),
        );
    }

    if (tasks.length < partner.taskCount) {
        tasksSection.addWidget(
            new LinkButton(_t("Show all"), new ActionCall(state, onSearchTasksClick)),
        );
    }

    card.addSection(tasksSection);
}
