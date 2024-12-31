import { Button, Group, Paper, TextInput, MantineProvider } from '@mantine/core';
import { IconCloudDownload } from '@tabler/icons-react';
import { useState, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

function ImportPanel({context}: {context: any}) {
    const pluginSettings = useMemo(() => context?.context?.settings ?? {}, [context]);
    if (!context?.user?.hasViewRole('purchase_order')) {
        console.log("has view role")
    }
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
 * Render the OrderHistoryPanel component
 * 
 * @param target - The target HTML element to render the panel into
 * @param context - The context object to pass to the panel
 */
export function renderPanel(target: HTMLElement, context: any) {

    createRoot(target).render(
        <MantineProvider>
            <ImportPanel context={context}/>
        </MantineProvider>
    )

}
