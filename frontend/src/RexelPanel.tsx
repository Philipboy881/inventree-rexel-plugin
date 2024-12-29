import { Button, Group, MantineProvider, Paper, TextInput } from '@mantine/core';
import { useCallback, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { IconSearch } from '@tabler/icons-react';

function RexelPanel() {
    const [searchText, setSearchText] = useState<string>('');

    const handleSearch = useCallback(() => {
        console.log("Search triggered with:", searchText);
        // Voeg hier logica toe om te zoeken of een API-aanroep te doen
    }, [searchText]);

    return (
        <Paper withBorder p="sm" m="sm">
            <Group gap="xs" justify="space-between" grow>
                <TextInput
                    label="Search"
                    placeholder="Enter search text"
                    value={searchText}
                    onChange={(e) => setSearchText(e.currentTarget.value)}
                />
                <Button leftSection={<IconSearch />} onClick={handleSearch}>
                    Search
                </Button>
            </Group>
        </Paper>
    );
}

/**
 * Render the RexelPanel component
 * 
 * @param target - The target HTML element to render the panel into
 */
export function renderPanel(target: HTMLElement) {
    createRoot(target).render(
        <MantineProvider>
            <RexelPanel />
        </MantineProvider>
    );
}
