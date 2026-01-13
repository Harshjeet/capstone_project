import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Activity, RefreshCw, Search, Filter, AlertCircle, CheckCircle, Info } from 'lucide-react';

const SystemAudit = () => {
    const [logs, setLogs] = useState([]);
    const [loading, setLoading] = useState(false);
    const [filter, setFilter] = useState('ALL');
    const [searchTerm, setSearchTerm] = useState('');

    const fetchLogs = async () => {
        setLoading(true);
        try {
            const res = await axios.get('/admin/system/logs');
            setLogs(res.data);
        } catch (err) {
            console.error("Failed to fetch logs", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchLogs();
        const interval = setInterval(fetchLogs, 30000); // Auto-refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const filteredLogs = logs.filter(log => {
        const matchesFilter = filter === 'ALL' || log.level === filter;
        const matchesSearch = !searchTerm ||
            (log.message && log.message.toLowerCase().includes(searchTerm.toLowerCase())) ||
            (log.module && log.module.toLowerCase().includes(searchTerm.toLowerCase()));
        return matchesFilter && matchesSearch;
    });

    const getLevelColor = (level) => {
        switch (level) {
            case 'ERROR': return '#ef4444';
            case 'WARNING': return '#f59e0b';
            case 'INFO': return '#10b981';
            default: return 'var(--text-muted)';
        }
    };

    const getLevelIcon = (level) => {
        switch (level) {
            case 'ERROR': return <AlertCircle size={14} />;
            case 'WARNING': return <AlertCircle size={14} />;
            case 'INFO': return <CheckCircle size={14} />;
            default: return <Info size={14} />;
        }
    };

    return (
        <div className="card" style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem', height: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <h3 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', margin: 0 }}>
                    <Activity size={20} style={{ color: 'var(--primary)' }} />
                    System Audit Stream
                </h3>
                <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <div style={{ position: 'relative' }}>
                        <Search size={16} style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                        <input
                            type="text"
                            placeholder="Search logs..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            style={{
                                padding: '0.5rem 1rem 0.5rem 2.5rem',
                                borderRadius: '8px',
                                border: '1px solid #e2e8f0',
                                fontSize: '0.875rem',
                                width: '200px'
                            }}
                        />
                    </div>
                    <select
                        value={filter}
                        onChange={(e) => setFilter(e.target.value)}
                        style={{ padding: '0.5rem', borderRadius: '8px', border: '1px solid #e2e8f0', fontSize: '0.875rem' }}
                    >
                        <option value="ALL">All Levels</option>
                        <option value="INFO">Info</option>
                        <option value="WARNING">Warning</option>
                        <option value="ERROR">Error</option>
                    </select>
                    <button
                        onClick={fetchLogs}
                        className={`btn ${loading ? 'loading' : ''}`}
                        style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}
                        disabled={loading}
                    >
                        <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
                        Refresh
                    </button>
                </div>
            </div>

            <div style={{
                backgroundColor: '#0f172a',
                borderRadius: '12px',
                padding: '1rem',
                maxHeight: '600px',
                overflowY: 'auto',
                boxShadow: 'inset 0 2px 4px 0 rgba(0, 0, 0, 0.05)'
            }}>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                    {filteredLogs.map((log, i) => (
                        <div key={i} style={{
                            display: 'flex',
                            gap: '1rem',
                            padding: '0.625rem',
                            borderBottom: '1px solid rgba(255,255,255,0.1)',
                            fontFamily: 'SFMono-Regular, Consolas, "Liberation Mono", Menlo, monospace',
                            fontSize: '0.8125rem',
                            transition: 'background 0.2s',
                            borderRadius: '4px',
                            color: '#e2e8f0'
                        }}>
                            <span style={{ color: '#94a3b8', width: '130px', flexShrink: 0 }}>
                                {log.timestamp?.split(',')[0]}
                            </span>
                            <span style={{
                                color: getLevelColor(log.level),
                                fontWeight: '700',
                                width: '70px',
                                display: 'flex',
                                alignItems: 'center',
                                gap: '0.25rem',
                                flexShrink: 0
                            }}>
                                {getLevelIcon(log.level)}
                                {log.level}
                            </span>
                            <span style={{ color: '#60a5fa', width: '120px', flexShrink: 0, fontStyle: 'italic' }}>
                                [{log.module}]
                            </span>
                            <span style={{ wordBreak: 'break-all' }}>{log.message}</span>
                        </div>
                    ))}
                    {filteredLogs.length === 0 && (
                        <div style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
                            {loading ? 'Streaming system events...' : 'No relevant audit logs found.'}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
};

export default SystemAudit;
