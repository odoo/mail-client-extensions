import { buildView } from "../views/index";
import { buildCreateTaskView } from "../views/create_task";
import { updateCard } from "./helpers";
import { UI_ICONS } from "./icons";
import { createKeyValueWidget, actionCall, notify } from "./helpers";
import { URLS } from "../const";
import { getOdooServerUrl } from "src/services/app_properties";
import { State } from "../models/state";
import { logEmail } from "../services/log_email";
import { _t } from "../services/translation";
import { truncate } from "../utils/format";

function onCreateTask(state: State) {
    return buildCreateTaskView(state);
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
    const tasks = partner.tasks;

    if (!tasks) {
        return;
    }

    const loggingState = State.getLoggingState(state.email.messageId);
    const tasksSection = CardService.newCardSection().setHeader("<b>" + _t("Tasks (%s)", tasks.length) + "</b>");
    const cids = state.odooCompaniesParameter;

    if (state.partner.id) {
        tasksSection.addWidget(
            CardService.newTextButton().setText(_t("Create")).setOnClickAction(actionCall(state, onCreateTask.name)),
        );

        for (let task of tasks) {
            let taskButton = null;
            if (loggingState["tasks"].indexOf(task.id) >= 0) {
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
                    task.projectName,
                    truncate(task.name, 35),
                    null,
                    null,
                    taskButton,
                    odooServerUrl + `/web#id=${task.id}&model=project.task&view_type=form${cids}`,
                ),
            );
        }
    } else if (state.canCreatePartner) {
        tasksSection.addWidget(CardService.newTextParagraph().setText(_t("Save the contact to create new tasks.")));
    } else {
        tasksSection.addWidget(
            CardService.newTextParagraph().setText(_t("The Contact needs to exist to create Task.")),
        );
    }

    card.addSection(tasksSection);
    return card;
}
