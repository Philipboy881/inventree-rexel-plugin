import { Button, Group, Paper, TextInput } from '@mantine/core';
import { IconCloudDownload } from '@tabler/icons-react';
import { useState } from 'react';
import { createRoot } from 'react-dom/client';

function ImportPanel() {
    // State voor de tekstvelden
    const [productNumber, setProductNumber] = useState('');
    const [pastNumber, setPastNumber] = useState('');

    // Functie om importactie te triggeren
    const handleImport = () => {
        if (productNumber && pastNumber) {
            console.log('Importeren met:', { productNumber, pastNumber });
            alert(`Gegevens geïmporteerd:\nProduct Nummer: ${productNumber}\nPast Nummer: ${pastNumber}`);
        } else {
            alert('Vul beide velden in voordat je importeert.');
        }
    };

    return (
        <Paper withBorder p="sm" m="sm">
            <Group gap="xs" grow>
                {/* Tekstvelden */}
                <TextInput
                    label="Product Nummer"
                    placeholder="Voer productnummer in"
                    value={productNumber}
                    onChange={(event) => setProductNumber(event.currentTarget.value)}
                />
                <TextInput
                    label="Past Nummer"
                    placeholder="Voer pastnummer in"
                    value={pastNumber}
                    onChange={(event) => setPastNumber(event.currentTarget.value)}
                />
                {/* Import knop */}
                <Button
                    leftSection={<IconCloudDownload />}
                    onClick={handleImport}
                >
                    Importeren
                </Button>
            </Group>
        </Paper>
    );
}

/**
 * Render het ImportPanel in een gegeven DOM-element.
 *
 * @param target - Het HTML-element waarin we dit paneel renderen.
 */
export function renderPanel(target: HTMLElement) {
    const root = createRoot(target);
    root.render(<ImportPanel />);
}
