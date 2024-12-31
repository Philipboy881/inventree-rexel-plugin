import { Button, Group, Paper, TextInput, MantineProvider, Alert, Text, Loader } from '@mantine/core';
import { IconCloudDownload } from '@tabler/icons-react';
import { useState, useMemo } from 'react';
import { QueryClient, useQuery } from '@tanstack/react-query'; // Import alleen useQuery en QueryClient
import { createRoot } from 'react-dom/client';

// Maak een nieuwe QueryClient aan
const queryClient = new QueryClient();

function ImportPanel({ context }: { context: any }) {
    const pluginSettings = useMemo(() => context?.context?.settings ?? {}, [context]);

    const [productNumber, setProductNumber] = useState('');
    const [partNumber, setPartNumber] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const IVENTREE_REXEL_URL = "plugin/inventree_rexel/rexel/";

    // Geef de queryClient door aan useQuery
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
    }, queryClient); // Het doorgeven van queryClient hier

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
            {(isSubmitting || isLoading) && (
                <div style={{ display: 'flex', justifyContent: 'center', marginTop: '20px' }}>
                    <Loader size="xl" />
                </div>
            )}

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
            {data && (
                <Paper mt="md" withBorder p="sm">
                    <Text>Import Results:</Text>
                    <pre>{JSON.stringify(data ?? {}, null, 2)}</pre>
                </Paper>
            )}
        </Paper>
    );
}

// Render de ImportPanel component zonder QueryClientProvider
export function renderPanel(target: HTMLElement, context: any) {
    createRoot(target).render(
        <MantineProvider>
            <ImportPanel context={context} />
        </MantineProvider>
    );
}
