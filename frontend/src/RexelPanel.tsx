import { Button, Group, Paper, TextInput, MantineProvider, Alert, LoadingOverlay, Text } from '@mantine/core';
import { IconCloudDownload } from '@tabler/icons-react';
import { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { createRoot } from 'react-dom/client';

function ImportPanel({ context }: { context: any }) {
    const pluginSettings = useMemo(() => context?.context?.settings ?? {}, [context]);

    // State voor invoervelden
    const [productNumber, setProductNumber] = useState('');
    const [partNumber, setPartNumber] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const IVENTREE_REXEL_URL = "plugin/inventree_rexel/rexel/";
    
    // Query om data op te halen
    const { data, isError, isLoading, refetch } = useQuery<{ 
        productNumber: string; 
        partNumber: string; 
        status: string; 
        message: string; 
    }>({
        queryKey: ['import-data', productNumber, partNumber],
        queryFn: async () => {
            const response = await context.api?.post(IVENTREE_REXEL_URL, {
                productNumber,
                partNumber,
            });
            return response?.data;
        },
        enabled: false, // Alleen uitvoeren als refetch wordt aangeroepen
    });

    // Functie om de importactie te triggeren
    const handleImport = async () => {
        if (!productNumber || !partNumber) {
            alert('Enter both fields before import.');
            return;
        }

        try {
            setIsSubmitting(true);
            await refetch();
        } catch (error) {
            alert('An error has occurred while getting your data while importing. ' + pluginSettings);
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Paper withBorder p="sm" m="sm" pos="relative">
            <LoadingOverlay visible={isSubmitting || isLoading} overlayBlur={2} />
            {isError && (
                <Alert color="red" title="Error">
                    An error has occurred while getting your data.
                </Alert>
            )}
            <Group gap="xs" grow>
                <TextInput
                    label="Product EAN, SKU, Type of description"
                    placeholder="Enter product data"
                    value={productNumber}
                    onChange={(event) => setProductNumber(event.currentTarget.value)}
                />
                <TextInput
                    label="New internal part number"
                    placeholder="Enter new part number"
                    value={partNumber}
                    onChange={(event) => setPartNumber(event.currentTarget.value)}
                />
                <Button
                    leftSection={<IconCloudDownload />}
                    onClick={handleImport}
                    disabled={isSubmitting || isLoading}
                >
                    Import
                </Button>
            </Group>
            {/* Weergave van ontvangen data */}
            {data && (
                <Paper mt="md" withBorder p="sm">
                    <Text>Import Results:</Text>
                    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
                </Paper>
            )}
        </Paper>
    );
}

/**
 * Render the ImportPanel component
 * 
 * @param target - The HTML element to render the panel into
 * @param context - The context object to pass to the panel
 */
export function renderPanel(target: HTMLElement, context: any) {
    createRoot(target).render(
        <MantineProvider>
            <ImportPanel context={context} />
        </MantineProvider>
    );
}
