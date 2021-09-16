import * as React from 'react';
import Task from '../../../../classes/Task';
import { _t } from '../../../../utils/Translator';
import api from '../../../api';
import Logger from '../../Log/Logger';
import '../../../../utils/ListItem.css';

type TaskListItemProps = {
    task: Task;
};

const TaskListItem = (props: TaskListItemProps) => {
    const openInOdoo = () => {
        const cids = this.context.getUserCompaniesString();
        let url = api.baseURL + `/web#id=${props.task.id}&model=project.task&view_type=form${cids}`;
        window.open(url, '_blank');
    };

    return (
        <div className="list-item-root-container" onClick={openInOdoo}>
            <div className="list-item-container">
                <div className="list-item-info-container">
                    <div className="list-item-title-text">{props.task.name}</div>
                    {props.task.projectName}
                </div>
                <Logger resId={props.task.id} model="project.task" tooltipContent={_t('Log Email Into Task')} />
            </div>
        </div>
    );
};

export default TaskListItem;
