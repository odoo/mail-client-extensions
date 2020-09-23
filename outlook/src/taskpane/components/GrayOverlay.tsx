import * as React from "react";
import './GrayOverlay.css';

export default class Progress extends React.Component {
    render() {
        return (<>
                    <div className='gray-overlay'/>
                    <img className='overlay-spinner'src='assets/spinner-2.gif'/>
            </>
        );
    }
}