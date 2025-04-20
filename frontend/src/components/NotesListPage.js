import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Card, Button, Row, Col, Spinner, Alert, Modal, Form } from 'react-bootstrap';
import '../styles/NotesListPage.css';
import { FaRobot, FaPlus } from 'react-icons/fa';

const API_URL = 'http://localhost:8000/api';

const NotesListPage = () => {
    const [notes, setNotes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showCategoryModal, setShowCategoryModal] = useState(false);
    const [newCategoryName, setNewCategoryName] = useState('');
    const [creatingCategory, setCreatingCategory] = useState(false);
    const navigate = useNavigate();

    const colorClasses = ['note-card-orange', 'note-card-yellow', 'note-card-purple', 'note-card-blue', 'note-card-green'];

    useEffect(() => {
        fetchNotes();
    }, []);

    const fetchNotes = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/notes/list`, {
                headers: { Authorization: token ? `Bearer ${token}` : '' }
            });
            setNotes(response.data.data || []);
        } catch (err) {
            console.error('Error fetching notes:', err);
            setError('Failed to fetch notes. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateNote = () => {
        navigate('/new');
    };

    const handleNoteClick = (noteId) => {
        navigate(`/edit/${noteId}`);
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
        });
    };

    const truncateContent = (content, maxLength = 100) => {
        if (!content) return '';
        return content.length > maxLength
            ? content.substring(0, maxLength) + '...'
            : content;
    };

    const getColorClass = (id) => {
        if (!id) return colorClasses[0];
        return colorClasses[id % colorClasses.length];
    };

    const handleCreateCategory = async (e) => {
        e.preventDefault();
        if (!newCategoryName.trim()) return;

        setCreatingCategory(true);
        try {
            const token = localStorage.getItem('token');
            await axios.post(
                `${API_URL}/categories/create`,
                { name: newCategoryName },
                { headers: { Authorization: token ? `Bearer ${token}` : '' } }
            );
            setNewCategoryName('');
            setShowCategoryModal(false);
            // Refresh categories list
            fetchNotes();
        } catch (err) {
            console.error('Error creating category:', err);
            setError('Failed to create category. Please try again.');
        } finally {
            setCreatingCategory(false);
        }
    };

    return (
        <Container className="notes-list-container py-5">
            <Row className="mb-4 align-items-center">
                <Col>
                    <h1 className="display-4 fw-bold text-primary">My Notes</h1>
                </Col>
                <Col className="text-end">
                    <div className="d-flex gap-2 justify-content-end">
                        <Button
                            variant="outline-primary"
                            className="rounded-pill"
                            onClick={() => navigate('/quizzes')}
                        >
                            <FaRobot className="me-2" />
                            My Quizzes
                        </Button>
                        <Button
                            variant="outline-primary"
                            className="rounded-pill"
                            onClick={() => setShowCategoryModal(true)}
                        >
                            <FaPlus className="me-2" />
                            New Category
                        </Button>
                        <Button
                            variant="primary"
                            onClick={handleCreateNote}
                            className="rounded-pill"
                        >
                            <FaPlus className="me-2" />
                            Create Note
                        </Button>
                    </div>
                </Col>
            </Row>

            {loading && (
                <div className="text-center my-5 py-5">
                    <Spinner animation="border" role="status" variant="primary">
                        <span className="visually-hidden">Loading...</span>
                    </Spinner>
                </div>
            )}

            {error && (
                <Alert variant="danger" className="rounded-pill">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    {error}
                </Alert>
            )}

            {!loading && notes.length === 0 && !error && (
                <div className="text-center my-5 py-5">
                    <div className="empty-state p-5 rounded-4 bg-light">
                        <i className="bi bi-journal-text display-1 text-muted mb-4"></i>
                        <h3 className="mb-3">No notes yet</h3>
                        <p className="text-muted mb-4">Start creating your first note to get started!</p>
                        <Button
                            variant="primary"
                            onClick={handleCreateNote}
                            className="px-4 py-2 rounded-pill"
                        >
                            Create Your First Note
                        </Button>
                    </div>
                </div>
            )}

            <Row xs={1} md={2} lg={3} className="g-4">
                {notes.map((note) => (
                    <Col key={note.id}>
                        <Card
                            className={`h-100 note-card ${getColorClass(note.id)}`}
                        >
                            <Card.Body className="d-flex flex-column">
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                    <Card.Title className="fw-bold mb-0">{note.title}</Card.Title>
                                    {note.is_ai_generated && (
                                        <span className="ai-badge">
                                            <FaRobot size={14} />
                                        </span>
                                    )}
                                </div>
                                <Card.Subtitle className="mb-3 text-muted">
                                    <i className="bi bi-calendar3 me-2"></i>
                                    {formatDate(note.updated_at || note.created_at)}
                                </Card.Subtitle>
                                <Card.Text className="flex-grow-1 mb-3">
                                    {truncateContent(note.content)}
                                </Card.Text>
                                {note.categories && note.categories.length > 0 && (
                                    <div className="note-categories mt-auto">
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
                            <Card.Footer className="bg-transparent border-top-0">
                                <Button
                                    variant="outline-primary"
                                    className="w-100 rounded-pill"
                                    onClick={() => navigate(`/notes/${note.id}`)}
                                >
                                    <i className="bi bi-eye me-2"></i>
                                    View Note
                                </Button>
                            </Card.Footer>
                        </Card>
                    </Col>
                ))}
            </Row>

            <Modal show={showCategoryModal} onHide={() => setShowCategoryModal(false)} centered>
                <Modal.Header closeButton>
                    <Modal.Title>Create New Category</Modal.Title>
                </Modal.Header>
                <Form onSubmit={handleCreateCategory}>
                    <Modal.Body>
                        <Form.Group>
                            <Form.Label>Category Name</Form.Label>
                            <Form.Control
                                type="text"
                                value={newCategoryName}
                                onChange={(e) => setNewCategoryName(e.target.value)}
                                placeholder="Enter category name"
                                required
                                className="rounded-pill"
                            />
                        </Form.Group>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="secondary"
                            onClick={() => setShowCategoryModal(false)}
                            className="rounded-pill"
                        >
                            Cancel
                        </Button>
                        <Button
                            variant="primary"
                            type="submit"
                            disabled={creatingCategory}
                            className="rounded-pill"
                        >
                            {creatingCategory ? (
                                <>
                                    <Spinner
                                        as="span"
                                        animation="border"
                                        size="sm"
                                        role="status"
                                        aria-hidden="true"
                                        className="me-2"
                                    />
                                    Creating...
                                </>
                            ) : (
                                'Create Category'
                            )}
                        </Button>
                    </Modal.Footer>
                </Form>
            </Modal>
        </Container>
    );
};

export default NotesListPage; 