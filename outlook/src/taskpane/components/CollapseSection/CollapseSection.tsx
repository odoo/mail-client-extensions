import * as React from "react";
import {faChevronDown, faChevronRight, faPlus} from "@fortawesome/free-solid-svg-icons";
import {FontAwesomeIcon} from "@fortawesome/react-fontawesome";
import "./CollapseSection.css";
import {ReactElement} from "react";


type CollapseSectionProps = {
    title: string;
    isCollapsed: boolean;
    onCollapseButtonClick: () => void;
    hasAddButton?: boolean;
    hasDropdownAddButton?: boolean,
    onAddButtonClick?: () => void;
    hideCollapseButton?: boolean;
    children: ReactElement;
}


/***
 * Class which handles a collapsable section
 */
class CollapseSection extends React.Component<CollapseSectionProps, {}>
{
    constructor(props, context) {
        super(props, context);
    }

    render() {
        let header;
        let content = null;
        let addButton = null;
        let collapseButton = null;
        if (this.props.hasAddButton)
        {
            let className = "collapse-section-button";
            if (this.props.hasDropdownAddButton) {
                className += " dropdown-collapse-section-button";
            }
            addButton = (<FontAwesomeIcon icon={faPlus} className={className} onClick={this.props.onAddButtonClick}/>);
        }

        if (!this.props.hideCollapseButton)
        {
            if (this.props.isCollapsed)
            {
                collapseButton = (
                    <FontAwesomeIcon className="collapse-section-button" icon={faChevronRight}
                                     onClick={this.props.onCollapseButtonClick}/>
                );
            }
            else
            {
                collapseButton = (
                    <FontAwesomeIcon className="collapse-section-button" icon={faChevronDown}
                                     onClick={this.props.onCollapseButtonClick}/>
                );
            }
        }

        if (this.props.isCollapsed)
        {
            header =
                (
                    <div className="section-top">
                        <div className="section-title-text">{this.props.title}</div>
                            <div>
                                    {addButton}
                                    {collapseButton}
                            </div>
                    </div>
                );
        }
        else
        {
            header =
                (
                    <div className="section-top">
                        <div className="section-title-text">{this.props.title}</div>
                        <div>
                            {addButton}
                            {collapseButton}
                        </div>
                    </div>
                );
            content = this.props.children;
        }


        return (
            <div className="section-card">
                {header}
                {content}
            </div>
        );
    }
}

export default CollapseSection;