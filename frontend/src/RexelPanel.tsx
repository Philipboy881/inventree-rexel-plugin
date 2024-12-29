import React from 'react';

const RexelPanel: React.FC = () => {
    const handleImportClick = async () => {
        try {
            const response = await fetch('/plugin/inventree_rexel/');
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            const data = await response.json();
            alert(data.message); // Toont "Hello World"
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    };

    return (
        <div>
            <button onClick={handleImportClick}>Import from Rexel</button>
        </div>
    );
};

export default RexelPanel;
