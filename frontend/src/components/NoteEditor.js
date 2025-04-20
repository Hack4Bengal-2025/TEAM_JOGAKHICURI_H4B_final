import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import { Container, Form, Button, Spinner, Alert, Row, Col } from 'react-bootstrap';
import '../styles/NoteEditor.css';
import { FaArrowLeft, FaTimes, FaSave, FaTrash, FaRobot, FaTags, FaFilePdf, FaUpload } from 'react-icons/fa';
import GenericModal from './GenericModal';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const NoteEditor = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const isNewNote = !id;

    const [note, setNote] = useState({
        title: '',
        content: '',
        categories: []
    });
    const [loading, setLoading] = useState(false);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState(null);
    const [successMessage, setSuccessMessage] = useState(null);
    const [categories, setCategories] = useState([]);
    const [selectedCategories, setSelectedCategories] = useState([]);

    // AI generation state
    const [showAiSection, setShowAiSection] = useState(false);
    const [userPrompt, setUserPrompt] = useState('');
    const [files, setFiles] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationError, setGenerationError] = useState('');

    const [showDeleteModal, setShowDeleteModal] = useState(false);

    useEffect(() => {
        if (id) {
            if (location.state?.note) {
                // If note data is passed from view page
                setNote(location.state.note);
                setSelectedCategories(location.state.note.categories || []);
            } else {
                // Fetch note data if not passed from view page
                fetchNote();
            }
        }
        fetchCategories();
    }, [id, location.state]);

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
                setSelectedCategories(response.data.data.categories || []);
            } else {
                throw new Error('Invalid response format');
            }
        } catch (err) {
            console.error('Error fetching note:', err);
            setError('Failed to load note. It may have been deleted or you may not have permission to edit it.');
        } finally {
            setLoading(false);
        }
    };

    const fetchCategories = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/categories/list`, {
                headers: { Authorization: token ? `Bearer ${token}` : '' }
            });
            if (response.data.success && response.data.data) {
                setCategories(response.data.data);
            }
        } catch (err) {
            console.error('Error fetching categories:', err);
        }
    };

    const handleInputChange = (e) => {
        const { name, value } = e.target;
        setNote(prev => ({
            ...prev,
            [name]: value
        }));
    };

    const handleCategoryToggle = (category) => {
        setSelectedCategories(prev => {
            const isSelected = prev.some(cat => cat.id === category.id);
            if (isSelected) {
                return prev.filter(cat => cat.id !== category.id);
            } else {
                return [...prev, category];
            }
        });
    };

    const saveNote = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setSuccessMessage(null);

        try {
            const token = localStorage.getItem('token');
            const noteData = {
                title: note.title,
                content: note.content,
                categories: selectedCategories.map(cat => cat.id)
            };

            let response;
            if (isNewNote) {
                response = await axios.post(`${API_URL}/notes/create`, noteData, { headers: { Authorization: token ? `Bearer ${token}` : '' } });
                setSuccessMessage('Note created successfully!');
            } else {
                response = await axios.put(`${API_URL}/notes/${id}`, noteData, { headers: { Authorization: token ? `Bearer ${token}` : '' } });
                setSuccessMessage('Note updated successfully!');
                navigate(`/note`);
            }

            if (isNewNote && response.data && response.data.data.id) {
                console.log("RESPONSE FROM NOTE CREATE API : ", response.data.data.id);
                setTimeout(() => {
                    navigate(`/note/${response.data.data.id}`, response.data.data);
                }, 1500);
            }
        } catch (err) {
            console.error('Error saving note:', err);
            setError(err.response?.data?.message || 'Failed to save note. Please try again.');
        } finally {
            setLoading(false);
            setSaving(false);
        }
    };

    const handleCancel = () => {
        navigate('/');
    };

    const handleDelete = async () => {
        if (!id || isNewNote) return;

        setLoading(true);
        setError(null);

        try {
            const token = localStorage.getItem('token');
            await axios.delete(`${API_URL}/notes/${id}`, {
                headers: { Authorization: token ? `Bearer ${token}` : '' }
            });
            navigate('/');
        } catch (err) {
            console.error('Error deleting note:', err);
            setError('Failed to delete note. Please try again.');
            setLoading(false);
        }
    };

    const handleFileChange = (e) => {
        const selectedFiles = Array.from(e.target.files);
        setFiles([...files, ...selectedFiles]);
    };

    const removeFile = (index) => {
        const updatedFiles = [...files];
        updatedFiles.splice(index, 1);
        setFiles(updatedFiles);
    };

    const generateAiNote = async () => {
        if (!userPrompt) {
            setGenerationError('Please enter a prompt for the AI.');
            return;
        }

        setIsGenerating(true);
        setGenerationError('');

        try {
            const token = localStorage.getItem('token');

            const formData = new FormData();
            formData.append('user_prompt_input', userPrompt);
            formData.append('rag_enabled', files.length > 0 ? 'true' : 'false');

            // Append files if any
            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            const response = await axios.post(
                `${API_URL}/notes/create-ai-note`,
                formData,
                {
                    headers: {
                        Authorization: token ? `Bearer ${token}` : '',
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            if (response.data && response.data.success) {
                const generatedNote = response.data.data;
                console.log('Generated note:', generatedNote); // Debug log
                // Hide AI section before navigation
                setShowAiSection(false);
                setUserPrompt(''); // Clear the prompt
                setFiles([]); // Clear any uploaded files
                // Navigate to the edit page with the generated note's ID
                navigate(`/notes/${generatedNote.id}/edit`);
            } else {
                setGenerationError(response.data?.message || 'Failed to generate note');
            }
        } catch (error) {
            console.error('Error generating AI note:', error);
            setGenerationError(
                'An error occurred: ' + (error.response?.data?.message || error.message)
            );
        } finally {
            setIsGenerating(false);
        }
    };

    if (loading && !note.title) {
        return (
            <Container className="text-center my-5 py-5">
                <Spinner animation="border" role="status" variant="primary">
                    <span className="visually-hidden">Loading...</span>
                </Spinner>
            </Container>
        );
    }

    return (
        <Container className="editor-container py-4">
            <div className="editor-header d-flex align-items-center gap-3 mb-4">
                <Button 
                    variant="outline-primary" 
                    className="back-button rounded-pill"
                    onClick={handleCancel}
                >
                    <FaArrowLeft className="me-2" />
                    Back to Notes
                </Button>
                <h1 className="display-4 fw-bold text-primary mb-0">
                    {isNewNote ? 'Create New Note' : 'Edit Note'}
                </h1>
            </div>

            {error && (
                <Alert variant="danger" className="rounded-pill mb-4">
                    <i className="bi bi-exclamation-triangle-fill me-2"></i>
                    {error}
                </Alert>
            )}
            {successMessage && (
                <Alert variant="success" className="rounded-pill mb-4">
                    <i className="bi bi-check-circle-fill me-2"></i>
                    {successMessage}
                </Alert>
            )}

            {/* Delete Confirmation Modal */}
            <GenericModal
                show={showDeleteModal}
                onClose={() => setShowDeleteModal(false)}
                onConfirm={handleDelete}
                title="Delete Note"
                body="Are you sure you want to delete this note? This action cannot be undone."
                confirmText="Delete"
                cancelText="Cancel"
                variant="danger"
            />

            <div className="editor-card rounded-4 p-4">
                {showAiSection ? (
                    <div className="ai-section">
                        <div className="d-flex justify-content-between align-items-center mb-4">
                            <h5 className="mb-0">
                                <FaRobot className="me-2" />
                                Generate with AI
                            </h5>
                            <Button 
                                variant="outline-primary" 
                                size="sm"
                                onClick={() => setShowAiSection(false)}
                            >
                                <FaTimes className="me-1" />
                                Close
                            </Button>
                        </div>

                        <div className="mb-4">
                            <Form.Label>Enter your prompt</Form.Label>
                            <Form.Control
                                as="textarea"
                                rows={3}
                                value={userPrompt}
                                onChange={(e) => setUserPrompt(e.target.value)}
                                placeholder="Describe what you want to generate..."
                                className="mb-3"
                            />
                        </div>

                        <div className="file-drop-zone mb-4">
                            <input
                                type="file"
                                id="file-upload"
                                accept=".pdf"
                                onChange={handleFileChange}
                                style={{ display: 'none' }}
                            />
                            <label htmlFor="file-upload" className="drop-zone">
                                <div className="drop-zone-content">
                                    <FaUpload className="mb-3" size={24} />
                                    <p className="mb-2">Drag & drop PDF files here</p>
                                    <p className="text-muted small">or click to browse</p>
                                </div>
                            </label>
                        </div>

                        {files.length > 0 && (
                            <div className="file-list mb-4">
                                {files.map((file, index) => (
                                    <div key={index} className="file-item">
                                        <div className="d-flex align-items-center">
                                            <FaFilePdf className="me-2" />
                                            <span className="file-name">{file.name}</span>
                                        </div>
                                        <Button
                                            variant="outline-danger"
                                            size="sm"
                                            onClick={() => removeFile(index)}
                                        >
                                            <FaTimes />
                                        </Button>
                                    </div>
                                ))}
                            </div>
                        )}

                        <Button
                            variant="primary"
                            onClick={generateAiNote}
                            disabled={isGenerating || (!userPrompt && files.length === 0)}
                            className="w-100"
                        >
                            {isGenerating ? (
                                <>
                                    <Spinner as="span" animation="border" size="sm" className="me-2" />
                                    Generating...
                                </>
                            ) : (
                                'Generate Note'
                            )}
                        </Button>

                        {generationError && (
                            <Alert variant="danger" className="mt-3">
                                {generationError}
                            </Alert>
                        )}
                    </div>
                ) : (
                    <Form onSubmit={saveNote}>
                        {!id && (
                            <div className="d-flex justify-content-end mb-4">
                                <Button
                                    variant="outline-primary"
                                    onClick={() => setShowAiSection(true)}
                                >
                                    <FaRobot className="me-2" />
                                    Generate with AI
                                </Button>
                            </div>
                        )}

                        <Form.Group className="mb-4">
                            <Form.Label className="fw-bold text-muted">Title</Form.Label>
                            <Form.Control
                                type="text"
                                name="title"
                                value={note.title}
                                onChange={handleInputChange}
                                placeholder="Enter note title"
                                required
                                className="rounded-pill"
                            />
                        </Form.Group>

                        <Form.Group className="mb-4">
                            <Form.Label className="fw-bold text-muted">Content</Form.Label>
                            <Form.Control
                                as="textarea"
                                name="content"
                                value={note.content}
                                onChange={handleInputChange}
                                placeholder="Enter note content"
                                rows={10}
                                className="rounded-4"
                            />
                        </Form.Group>

                        <Form.Group className="mb-4">
                            <Form.Label className="fw-bold text-muted d-flex align-items-center">
                                <FaTags className="me-2" />
                                Categories
                            </Form.Label>
                            <div className="categories-container p-3 rounded-4">
                                <div className="d-flex flex-wrap gap-2">
                                    {categories.map(category => (
                                        <button
                                            key={category.id}
                                            type="button"
                                            className={`category-button rounded-pill ${
                                                selectedCategories.some(cat => cat.id === category.id)
                                                    ? 'btn-primary'
                                                    : 'btn-outline-primary'
                                            }`}
                                            onClick={() => handleCategoryToggle(category)}
                                        >
                                            {category.name}
                                            {category.is_ai_generated && (
                                                <i className="bi bi-robot ms-1"></i>
                                            )}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </Form.Group>

                        <div className="d-flex justify-content-end gap-2">
                            {!isNewNote && (
                                <Button
                                    variant="outline-danger"
                                    onClick={() => setShowDeleteModal(true)}
                                    className="rounded-pill"
                                    disabled={saving}
                                >
                                    <FaTrash className="me-2" />
                                    Delete
                                </Button>
                            )}
                            <Button
                                variant="primary"
                                type="submit"
                                className="rounded-pill"
                                disabled={saving}
                            >
                                {saving ? (
                                    <>
                                        <Spinner
                                            as="span"
                                            animation="border"
                                            size="sm"
                                            role="status"
                                            aria-hidden="true"
                                            className="me-2"
                                        />
                                        Saving...
                                    </>
                                ) : (
                                    <>
                                        <FaSave className="me-2" />
                                        Save Note
                                    </>
                                )}
                            </Button>
                        </div>
                    </Form>
                )}
            </div>
        </Container>
    );
};

export default NoteEditor; 