import { buildView } from "../views/index";
import { buildCreateTaskView } from "../views/create_task";
import { pushCard, updateCard } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify } from "./helpers";
import { getOdooServerUrl } from "src/services/app_properties";
import { State } from "../models/state";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";
import { getOdooRecordURL } from "src/services/odoo_redirection";
import { buildSearchRecordView } from "../views/search_records";

function onCreateTask(state: State) {
    return pushCard(buildCreateTaskView(state));
}

function onSearchClick(state: State) {
    return buildSearchRecordView(
        state,
        "project.task",
        _t("Tasks"),
        _t("Log the email on the task"),
        _t("Email already logged on the task"),
        "projectName",
        "",
        true,
        state.partner.tasks,
    );
}

function onLogEmailOnTask(state: State, parameters: any) {
    const taskId = parameters.taskId;

    if (State.checkLoggingState(state.email.messageId, "project.task", taskId)) {
        const error = logEmail(taskId, "project.task", state.email);
        if (error.code) {
            return notify(error.message);
        }
        State.setLoggingState(state.email.messageId, "project.task", taskId);
        return updateCard(buildView(state));
    }
    return notify(_t("Email already logged on the task"));
}

function onEmailAlreradyLoggedOnTask() {
    return notify(_t("Email already logged on the task"));
}

export function buildTasksView(state: State, card: Card) {
    const odooServerUrl = getOdooServerUrl();
    const partner = state.partner;
    if (!partner.tasks) {
        return;
    }

    const tasks = [...partner.tasks].splice(0, 5);

    const loggingState = State.getLoggingState(state.email.messageId);
    const tasksSection = CardService.newCardSection();

    const searchButton = CardService.newImageButton()
        .setAltText(_t("Search Tasks"))
        .setIconUrl(UI_ICONS.search)
        .setOnClickAction(actionCall(state, onSearchClick.name));

    const title = partner.taskCount ? _t("Tasks (%s)", partner.taskCount) : _t("Tasks");
    const widget = CardService.newDecoratedText().setText("<b>" + title + "</b>");
    widget.setButton(searchButton);
    tasksSection.addWidget(widget);

    const createButton = CardService.newTextButton()
        .setText(_t("New"))
        .setOnClickAction(actionCall(state, onCreateTask.name));
    tasksSection.addWidget(createButton);

    for (let task of tasks) {
        let taskButton = null;
        if (loggingState["project.task"].indexOf(task.id) >= 0) {
            taskButton = CardService.newImageButton()
                .setAltText(_t("Email already logged on the task"))
                .setIconUrl(UI_ICONS.email_logged)
                .setOnClickAction(actionCall(state, onEmailAlreradyLoggedOnTask.name));
        } else {
            taskButton = CardService.newImageButton()
                .setAltText(_t("Log the email on the task"))
                .setIconUrl(UI_ICONS.email_in_odoo)
                .setOnClickAction(
                    actionCall(state, onLogEmailOnTask.name, {
                        taskId: task.id,
                    }),
                );
        }

        tasksSection.addWidget(
            createKeyValueWidget(
                null,
                task.name,
                null,
                task.projectName,
                taskButton,
                getOdooRecordURL("project.task", task.id),
            ),
        );
    }

    if (tasks.length < partner.taskCount) {
        tasksSection.addWidget(
            CardService.newTextButton()
                .setText(_t("Show all"))
                .setTextButtonStyle(CardService.TextButtonStyle["BORDERLESS"])
                .setOnClickAction(actionCall(state, onSearchClick.name)),
        );
    }

    card.addSection(tasksSection);
    return card;
}
