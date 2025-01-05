import { Code, Button, Group, Paper, TextInput, MantineProvider, Alert, Text, Loader } from '@mantine/core';
import { IconCloudDownload } from '@tabler/icons-react';
import { useState, useMemo } from 'react';
import { QueryClient, useQuery } from '@tanstack/react-query';
import { createRoot } from 'react-dom/client';

// Maak een nieuwe QueryClient aan
const queryClient = new QueryClient();

function ImportPanel({ context }: { context: any }) {
    const pluginSettings = useMemo(() => context?.context?.settings ?? {}, [context]);

    const [product_number, setproduct_number] = useState('');
    const [part_number, setpart_number] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);

    const IVENTREE_REXEL_URL = "plugin/inventree_rexel/rexel/";

    const { data, isError, isLoading, refetch } = useQuery<{
        product_number: string;
        part_number: string;
        status: string;
        message: string;
    }>(
        {
            queryKey: ['import-data', product_number, part_number],
            queryFn: async () => {
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 10000);

                try {
                    const response = await context.api?.post(IVENTREE_REXEL_URL, {
                        product_number,
                        part_number,
                        signal: controller.signal,
                    });
                    return response?.data;
                } finally {
                    clearTimeout(timeoutId);
                }
            },
            enabled: false,
        },
        queryClient
    );

    const handleImport = async () => {
        if (!product_number || !part_number) {
            alert('Enter both fields before import.');
            return;
        }

        try {
            setIsSubmitting(true);
            await refetch();
        } catch (error: any) {
            if (error.name === 'AbortError') {
                alert('The request timed out. Please try again. ' + pluginSettings);
            } else {
                alert('An error has occurred while importing data.');
            }
        } finally {
            setIsSubmitting(false);
        }
    };

    return (
        <Paper withBorder p="sm" m="sm" pos="relative">
            {isError && (
                <Alert color="red" title="Error">
                    An error has occurred while getting your data.
                </Alert>
            )}

            <Group gap="xs" grow>
                <TextInput
                    label="Product EAN, SKU, Type of description"
                    placeholder="Enter product data"
                    value={product_number}
                    onChange={(event) => setproduct_number(event.currentTarget.value)}
                />
                <TextInput
                    label="New internal part number"
                    placeholder="Enter new part number"
                    value={part_number}
                    onChange={(event) => setpart_number(event.currentTarget.value)}
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
                    <Code block>
                        {JSON.stringify(data ?? {}, null, 2)}
                    </Code>
                </Paper>
            )}

            {(isSubmitting || isLoading) && (
                <div
                    style={{
                        position: 'absolute',
                        bottom: '20px',
                        left: '50%',
                        transform: 'translateX(-50%)',
                        display: 'flex',
                        justifyContent: 'center',
                        width: '100%',
                    }}
                >
                    <Loader size="xl" />
                </div>
            )}
        </Paper>
    );
}

// Render de ImportPanel component zonder QueryClientProvider
export function renderPanel(target: HTMLElement, context: any) {
    const isDarkMode = context?.theme?.dark ?? false;

    createRoot(target).render(
        <MantineProvider
            theme={{
                colorScheme: isDarkMode ? 'dark' : 'light', // Stel de kleurmodus in via het theme-object
            }}
        >
            <ImportPanel context={context} />
        </MantineProvider>
    );
}
