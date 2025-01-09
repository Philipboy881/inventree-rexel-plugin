import {
    Accordion,
    Button,
    TextInput,
    MantineProvider,
    Alert,
    Text,
    Loader,
    Stack,
    Code,
  } from '@mantine/core';
  import { useState } from 'react';
  import { IconCloudDownload } from '@tabler/icons-react';
  import { QueryClient, useQuery } from '@tanstack/react-query';
  import { createRoot } from 'react-dom/client';
  import React from 'react';


  // Maak een nieuwe QueryClient aan
  const queryClient = new QueryClient();
  
  function ImportPanel({ context }: { context: any }) {
    const [product_number, setProductNumber] = useState('');
    const [part_number, setPartNumber] = useState('');
    const [isSubmitting, setIsSubmitting] = useState(false);
  
    const IVENTREE_REXEL_URL = 'plugin/inventree_rexel/rexel/';
  
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
          alert('The request timed out. Please try again.');
        } else {
          alert('An error has occurred while importing data.');
        }
      } finally {
        setIsSubmitting(false);
      }
    };
  
    return (
      <Accordion defaultValue="import-panel">
        <Accordion.Item value="import-panel">
          <Accordion.Control>Import Data</Accordion.Control>
          <Accordion.Panel>
            {isError && (
              <Alert color="red" title="Error">
                An error has occurred while getting your data.
              </Alert>
            )}
  
            <Stack gap="xs">
              <TextInput
                label="Product EAN, SKU, Type of description"
                placeholder="Enter product data"
                value={product_number}
                onChange={(event) => setProductNumber(event.currentTarget.value)}
              />
              <TextInput
                label="New internal part number"
                placeholder="Enter new part number"
                value={part_number}
                onChange={(event) => setPartNumber(event.currentTarget.value)}
              />
              <Button
                leftSection={<IconCloudDownload />}
                onClick={handleImport}
                disabled={isSubmitting || isLoading}
              >
                Import
              </Button>
            </Stack>
  
            {data && (
              <div style={{ marginTop: '16px' }}>
                <Text>Import Results:</Text>
                <Code block>{JSON.stringify(data ?? {}, null, 2)}</Code>
              </div>
            )}
  
            {(isSubmitting || isLoading) && (
              <div style={{ textAlign: 'center', marginTop: '20px' }}>
                <Loader size="xl" />
              </div>
            )}
          </Accordion.Panel>
        </Accordion.Item>
      </Accordion>
    );
  }
  
  // Render de ImportPanel component
  export function renderPanel(target: HTMLElement, context: any) {
    createRoot(target).render(
      <MantineProvider>
        <ImportPanel context={context} />
      </MantineProvider>
    );
  }
  