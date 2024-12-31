import { Button, Group, Paper, TextInput, MantineProvider } from '@mantine/core';
import { IconCloudDownload } from '@tabler/icons-react';
import { useState, useMemo } from 'react';
import { createRoot } from 'react-dom/client';

function ImportPanel({context}: {context: any}) {
    const pluginSettings = useMemo(() => context?.context?.settings ?? {}, [context]);
    if (!pluginSettings.PURCHASE_ORDER_HISTORY) {
        console.log("Purchase = false")
    }
        
    
    // State voor de tekstvelden
    const [productNumber, setProductNumber] = useState('');
    const [partNumber, setpartNumber] = useState('');

    // Functie om importactie te triggeren
    const handleImport = () => {
        if (productNumber && partNumber) {
            










            console.log('Importeren met:', { productNumber, partNumber });
            alert(`Gegevens geïmporteerd:\nProduct Nummer: ${productNumber}\nPart Nummer: ${partNumber}`);
        } else {
            alert('Vul beide velden in voordat je importeert.');
        }
    };

    return (
        <Paper withBorder p="sm" m="sm">
            <Group gap="xs" grow>
                {/* Tekstvelden */}
                <TextInput
                    label="enter Product ean, sku, type, description"
                    placeholder="enter product data"
                    value={productNumber}
                    onChange={(event) => setProductNumber(event.currentTarget.value)}
                />
                <TextInput
                    label="New internal part nummer"
                    placeholder="enter new partnummer"
                    value={partNumber}
                    onChange={(event) => setpartNumber(event.currentTarget.value)}
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
