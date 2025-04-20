import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Button, Spinner, Alert, Card } from 'react-bootstrap';
import '../styles/NoteViewPage.css';
import { FaArrowLeft, FaEdit, FaRobot, FaTags } from 'react-icons/fa';
import Markdown from 'react-markdown'

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const NoteViewPage = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [note, setNote] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchNote();
    }, [id]);

    const fetchNote = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/notes/${id}`, {
                headers: { Authorization: token ? `Bearer ${token}` : '' }
            });
            if (response.data.success && response.data.data) {
                setNote(response.data.data);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (err) {
            console.error('Error fetching note:', err);
            setError('Failed to load note. It may have been deleted or you may not have permission to view it.');
        } finally {
            setLoading(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    if (loading) {
        return (
            <Container className="text-center my-5 py-5">
                <Spinner animation="border" role="status" variant="primary">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
            </Container>
        );
    }

    if (error) {
        return (
            <Container className="my-5">
                <Alert variant="danger" className="rounded-pill">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    {error}
                </Alert>
            </Container>
        );
    }

    return (
        <Container className="note-view-container py-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <Button 
                    variant="outline-primary" 
                    className="rounded-pill"
                    onClick={() => navigate('/')}
                >
                    <FaArrowLeft className="me-2" />
                    Back to Notes
                </Button>
                <Button
                    variant="primary"
                    className="rounded-pill"
                    onClick={() => navigate(`/notes/${id}/edit`, { state: { note } })}
                >
                    <FaEdit className="me-2" />
                    Edit Note
                </Button>
            </div>

            <Card className="note-card rounded-4 shadow-sm">
                <Card.Body className="p-4">
                    <div className="d-flex justify-content-between align-items-start mb-3">
                        <h1 className="display-5 fw-bold text-primary mb-0"><Markdown children={note.title} /></h1>
                        {note.is_ai_generated && (
                            <span className="ai-badge">
                                <FaRobot className="me-1" />
                                AI Generated
                            </span>
                        )}
                    </div>

                    <div className="text-muted mb-4">
                        <i className="bi bi-calendar3 me-2"></i>
                        Created: {formatDate(note.created_at)}
                        {note.updated_at !== note.created_at && (
                            <span className="ms-3">
                                <i className="bi bi-arrow-clockwise me-2"></i>
                                Updated: {formatDate(note.updated_at)}
                            </span>
                        )}
                    </div>

                    <div className="note-content mb-4">
                        <Markdown children={note.content} />
                    </div>

                    {note.categories && note.categories.length > 0 && (
                        <div className="note-categories">
                            <h5 className="fw-bold text-muted d-flex align-items-center mb-3">
                                <FaTags className="me-2" />
                                Categories
                            </h5>
                            <div className="d-flex flex-wrap gap-2">
                                {note.categories.map(category => (
                                    <span 
                                        key={category.id} 
                                        className="category-tag"
                                    >
                                        {category.name}
                                        {category.is_ai_generated && (
                                            <FaRobot className="ms-1" size={10} />
                                        )}
                                    </span>
                                ))}
                            </div>
                        </div>
                    )}
                </Card.Body>
            </Card>
        </Container>
    );
};

export default NoteViewPage; 