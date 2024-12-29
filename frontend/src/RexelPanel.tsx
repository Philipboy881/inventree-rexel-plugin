import React, { useState } from 'react';

const RexelPanel: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Functie om de zoekopdracht naar de API te sturen
  const handleSearch = async () => {
    if (!query) return;
  
    setLoading(true);
    setError(null);
  
    try {
      // Zorg ervoor dat je de juiste API aanroept met de zoekterm
      const response = await fetch(`/rexel/?query=${query}`);
      const data = await response.json();
  
      if (response.ok) {
        setResults(data.results);  // Zet de ontvangen zoekresultaten in de state
      } else {
        setError(data.error || 'An error occurred');
      }
    } catch (error) {
      setError('Failed to fetch data');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <h1>Rexel Producten Zoeken</h1>
      <div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Zoek op product"
        />
        <button onClick={handleSearch} disabled={loading}>
          {loading ? 'Zoeken...' : 'Zoek'}
        </button>
      </div>

      {error && <div style={{ color: 'red' }}>{error}</div>}

      <div>
        {results.length > 0 ? (
          <ul>
            {results.map((item, index) => (
              <li key={index}>
                <strong>{item.name}</strong> - {item.price} EUR
              </li>
            ))}
          </ul>
        ) : (
          <p>Geen resultaten gevonden</p>
        )}
      </div>
    </div>
  );
};

export default RexelPanel;
