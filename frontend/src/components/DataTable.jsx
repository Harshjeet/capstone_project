import React from 'react';

const DataTable = ({ title, data, columns, isLoading }) => {
    if (isLoading) return <div className="loading">Loading data...</div>;
    if (!data || data.length === 0) return <div className="empty-state">No records found.</div>;

    // Auto-generate columns if not provided
    const cols = columns || Object.keys(data[0]).filter(key => key !== 'id' && key !== '_id').slice(0, 5);

    return (
        <div className="card">
            <div style={{ borderBottom: '1px solid #e2e8f0', padding: '1rem 1.5rem', backgroundColor: '#f8fafc' }}>
                <h3 style={{ fontWeight: '600', color: 'var(--text)', margin: '0' }}>{title} ({data.length})</h3>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.875rem' }}>
                    <thead>
                        <tr>
                            {cols.map(col => (
                                <th key={col.key || col} style={{
                                    backgroundColor: '#f8fafc',
                                    color: 'var(--text-muted)',
                                    fontWeight: '500',
                                    padding: '0.75rem 1rem',
                                    borderBottom: '1px solid #e2e8f0',
                                    textTransform: 'uppercase',
                                    fontSize: '0.75rem',
                                    letterSpacing: '0.05em',
                                    textAlign: 'left'
                                }}>
                                    {col.label || col}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {data.map((row, idx) => (
                            <tr key={idx}>
                                {cols.map(col => {
                                    const key = col.key || col;
                                    let val = row[key];

                                    // Handle nested objects simply
                                    if (typeof val === 'object' && val !== null) {
                                        val = JSON.stringify(val).substring(0, 30) + "...";
                                    }

                                    return (
                                        <td key={key} style={{
                                            padding: '0.75rem 1rem',
                                            borderBottom: '1px solid #e2e8f0',
                                            color: 'var(--text)'
                                        }}>
                                            {val}
                                        </td>
                                    );
                                })}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default DataTable;
