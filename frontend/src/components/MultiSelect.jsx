import React, { useState, useRef, useEffect } from 'react';
import { ChevronDown, X, Check, Search } from 'lucide-react';

const MultiSelect = ({ options, selected, onChange, placeholder = "Select options...", label }) => {
    const [isOpen, setIsOpen] = useState(false);
    const [searchTerm, setSearchTerm] = useState('');
    const dropdownRef = useRef(null);

    const filteredOptions = options.filter(option =>
        option.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const toggleOption = (option) => {
        const newSelected = selected.includes(option)
            ? selected.filter(item => item !== option)
            : [...selected, option];
        onChange(newSelected);
    };

    const removeOption = (e, option) => {
        e.stopPropagation();
        onChange(selected.filter(item => item !== option));
    };

    useEffect(() => {
        const handleClickOutside = (event) => {
            if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
                setIsOpen(false);
            }
        };
        document.addEventListener('mousedown', handleClickOutside);
        return () => document.removeEventListener('mousedown', handleClickOutside);
    }, []);

    return (
        <div className="multi-select-container" ref={dropdownRef}>
            {label && <label className="form-label">{label}</label>}
            <div
                className={`multi-select-trigger ${isOpen ? 'active' : ''}`}
                onClick={() => setIsOpen(!isOpen)}
            >
                <div className="selected-tags">
                    {selected.length > 0 ? (
                        selected.map(item => (
                            <span key={item} className="select-tag">
                                {item}
                                <button onClick={(e) => removeOption(e, item)} className="remove-tag-btn">
                                    <X size={12} />
                                </button>
                            </span>
                        ))
                    ) : (
                        <span className="placeholder">{placeholder}</span>
                    )}
                </div>
                <ChevronDown className={`chevron-icon ${isOpen ? 'rotate' : ''}`} size={18} />
            </div>

            {isOpen && (
                <div className="multi-select-dropdown">
                    <div className="search-box">
                        <Search size={16} className="search-icon" />
                        <input
                            type="text"
                            placeholder="Search..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            onClick={(e) => e.stopPropagation()}
                            autoFocus
                        />
                    </div>
                    <div className="options-list">
                        {filteredOptions.length > 0 ? (
                            filteredOptions.map(option => (
                                <div
                                    key={option}
                                    className={`option-item ${selected.includes(option) ? 'selected' : ''}`}
                                    onClick={() => toggleOption(option)}
                                >
                                    <div className="checkbox">
                                        {selected.includes(option) && <Check size={12} color="white" />}
                                    </div>
                                    <span className="option-label">{option}</span>
                                </div>
                            ))
                        ) : (
                            <div className="no-options">No results found</div>
                        )}
                    </div>
                </div>
            )}
        </div>
    );
};

export default MultiSelect;
