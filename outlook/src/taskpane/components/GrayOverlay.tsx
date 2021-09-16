import * as React from 'react';
import './GrayOverlay.css';

const Progress = () => {
    return (
        <>
            <div className="gray-overlay" />
            <img className="overlay-spinner" src="assets/spinner-2.gif" />
        </>
    );
};

export default Progress;
