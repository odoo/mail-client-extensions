import * as React from 'react';
import Partner from '../../../../classes/Partner';
import Project from '../../../../classes/Project';
import Task from '../../../../classes/Task';
import { ContentType, HttpVerb, sendHttpRequest } from '../../../../utils/httpRequest';
import { _t } from '../../../../utils/Translator';
import CollapseSection from '../../CollapseSection/CollapseSection';
import TaskListItem from '../TaskList/TaskListItem';
import api from '../../../api';
import AppContext from '../../AppContext';
import { Callout, DirectionalHint } from 'office-ui-fabric-react';
import SelectProjectDropdown from './SelectProjectDropdown';

type TasksSectionProps = {
    partner: Partner;
};

type TasksSectionState = {
    tasks: Task[];
    isCollapsed: boolean;
    isProjectCalloutOpen: boolean;
    key: number;
};

class TasksSection extends React.Component<TasksSectionProps, TasksSectionState> {
    constructor(props, context) {
        super(props, context);
        let isCollapsed = true;
        if (props.partner.tasks && props.partner.tasks.length > 0) {
            isCollapsed = false;
        }
        this.state = {
            tasks: this.props.partner.tasks,
            isCollapsed: isCollapsed,
            isProjectCalloutOpen: false,
            key: Math.random(),
        };
    }

    private toggleProjectCallout = () => {
        this.setState({ isProjectCalloutOpen: !this.state.isProjectCalloutOpen });
    };

    private closeProjectCallout = () => {
        this.setState({ isProjectCalloutOpen: false });
    };

    private onCollapseButtonClick = () => {
        this.setState({ isCollapsed: !this.state.isCollapsed });
    };

    private onProjectSelected = (project: Project): void => {
        this.closeProjectCallout();
        this.createTask(project);
    };

    private createTask = (project: Project) => {
        Office.context.mailbox.item.body.getAsync(Office.CoercionType.Html, (result) => {
            const message = result.value.split('<div id="x_appendonsend"></div>')[0]; // Remove the history and only log the most recent message.
            const subject = Office.context.mailbox.item.subject;

            const taskValues = {
                partner_id: this.props.partner.id,
                email_body: message,
                email_subject: subject,
                project_id: project.id,
            };

            const createTaskRequest = sendHttpRequest(
                HttpVerb.POST,
                api.baseURL + api.createTask,
                ContentType.Json,
                this.context.getConnectionToken(),
                taskValues,
                true,
            );
            createTaskRequest.promise
                .then((response) => {
                    const parsed = JSON.parse(response);
                    if (parsed['error']) {
                        this.context.showTopBarMessage();
                        return;
                    } else {
                        const cids = this.context.getUserCompaniesString();
                        const action = 'project_mail_plugin.project_task_action_form_edit';
                        const url =
                            api.baseURL +
                            `/web#action=${action}&id=${parsed.result.task_id}&model=project.task&view_type=form${cids}`;
                        window.open(url);
                    }
                })
                .catch((error) => {
                    this.context.showHttpErrorMessage(error);
                });
        });
    };

    render() {
        let tasksExpanded = null;

        let title = _t('Tasks');

        if (!this.props.partner.isAddedToDatabase()) {
            if (!this.state.isCollapsed) {
                tasksExpanded = <div className="list-text">{_t('Save Contact to create new Tasks.')}</div>;
            }
        } else {
            if (!this.state.isCollapsed) {
                let tasksContent = null;
                if (this.state.tasks.length > 0) {
                    const tasks = this.state.tasks;
                    tasksContent = tasks.map((task) => {
                        return <TaskListItem task={task} key={task.id} />;
                    });
                } else {
                    tasksContent = <div className="list-text">{_t('No tasks found for this contact.')}</div>;
                }
                tasksExpanded = <div className="section-content">{tasksContent}</div>;
            }
        }

        if (this.state.tasks) title = _t('Tasks (%(count)s)', { count: this.state.tasks.length });

        let callout = null;
        if (this.state.isProjectCalloutOpen) {
            callout = (
                <Callout
                    directionalHint={DirectionalHint.bottomRightEdge}
                    directionalHintFixed={true}
                    onDismiss={() => this.setState({ isProjectCalloutOpen: false })}
                    preventDismissOnScroll={true}
                    setInitialFocus={true}
                    doNotLayer={true}
                    gapSpace={0}
                    role="alertdialog"
                    target=".dropdown-collapse-section-button">
                    <SelectProjectDropdown partner={this.props.partner} onProjectClick={this.onProjectSelected} />
                </Callout>
            );
        }
        return (
            <>
                <CollapseSection
                    onCollapseButtonClick={this.onCollapseButtonClick}
                    isCollapsed={this.state.isCollapsed}
                    title={title}
                    hasAddButton={this.props.partner.isAddedToDatabase()}
                    hasDropdownAddButton={true}
                    onAddButtonClick={this.toggleProjectCallout}>
                    {tasksExpanded}
                </CollapseSection>
                {callout}
            </>
        );
    }
}

TasksSection.contextType = AppContext;
export default TasksSection;
