import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { Container, Card, Button, Row, Col, Spinner, Alert } from 'react-bootstrap';
import { FaRobot, FaPlus } from 'react-icons/fa';
import '../styles/QuizListPage.css';

const API_URL = 'http://localhost:8000/api';

const QuizListPage = () => {
    const [quizzes, setQuizzes] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const colorClasses = ['quiz-card-orange', 'quiz-card-yellow', 'quiz-card-purple', 'quiz-card-blue', 'quiz-card-green'];

    useEffect(() => {
        fetchQuizzes();
    }, []);

    const fetchQuizzes = async () => {
        setLoading(true);
        setError(null);
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/quizzes/list`, {
                headers: { Authorization: token ? `Bearer ${token}` : '' }
            });

            // Clear the quizzes array to avoid duplicates
            setQuizzes([]);

            // Fetch detailed data for each quiz
            const quizPromises = response.data.data.map(async quiz => {
                try {
                    const quiz_data = await axios.get(`${API_URL}/quizzes/${quiz.id}/view`, {
                        headers: { Authorization: token ? `Bearer ${token}` : '' }
                    });
                    return quiz_data.data.data;
                } catch (err) {
                    console.error(`Error fetching quiz ${quiz.id}:`, err);
                    return null;
                }
            });

            // Wait for all requests to complete
            const quizDetails = await Promise.all(quizPromises);

            // Filter out any failed requests
            const validQuizzes = quizDetails.filter(quiz => quiz !== null);
            setQuizzes(validQuizzes);
        } catch (err) {
            console.error('Error fetching quizzes:', err);
            setError('Failed to fetch quizzes. Please try again later.');
        } finally {
            setLoading(false);
        }
    };

    const handleCreateQuiz = () => {
        navigate('/quiz/new');
    };

    const handleQuizClick = (quizId) => {
        navigate(`/quiz/${quizId}`);
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

    const getColorClass = (id) => {
        if (!id) return colorClasses[0];
        return colorClasses[id % colorClasses.length];
    };

    return (
        <Container className="quiz-list-container py-5">
            <Row className="mb-4 align-items-center">
                <Col>
                    <h1 className="display-4 fw-bold text-primary">My Quizzes</h1>
                </Col>
                <Col className="text-end">
                    <Button
                        variant="primary"
                        onClick={handleCreateQuiz}
                        className="rounded-pill"
                    >
                        <FaPlus className="me-2" />
                        Create Quiz
                    </Button>
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

            {!loading && quizzes.length === 0 && !error && (
                <div className="text-center my-5 py-5">
                    <div className="empty-state p-5 rounded-4 bg-light">
                        <i className="bi bi-question-circle display-1 text-muted mb-4"></i>
                        <h3 className="mb-3">No quizzes yet</h3>
                        <p className="text-muted mb-4">Start creating your first quiz to test your knowledge!</p>
                        <Button
                            variant="primary"
                            onClick={handleCreateQuiz}
                            className="px-4 py-2 rounded-pill"
                        >
                            Create Your First Quiz
                        </Button>
                    </div>
                </div>
            )}

            <Row xs={1} md={2} lg={3} className="g-4">
                {quizzes.map((quiz) => (
                    <Col key={quiz.id}>
                        <Card
                            className={`h-100 quiz-card ${getColorClass(quiz.id)}`}
                        >
                            <Card.Body className="d-flex flex-column">
                                <div className="d-flex justify-content-between align-items-start mb-2">
                                    <Card.Title className="fw-bold mb-0">{quiz.title}</Card.Title>
                                    {quiz.is_ai_generated && (
                                        <span className="ai-badge">
                                            <FaRobot size={14} />
                                        </span>
                                    )}
                                </div>
                                <Card.Subtitle className="mb-3 text-muted">
                                    <i className="bi bi-calendar3 me-2"></i>
                                    {formatDate(quiz.created_at)}
                                </Card.Subtitle>
                                <Card.Text className="flex-grow-1 mb-3">
                                    {quiz.questions?.length} Questions
                                </Card.Text>
                            </Card.Body>
                            <Card.Footer className="bg-transparent border-top-0">
                                <Button
                                    variant="outline-primary"
                                    className="w-100 rounded-pill"
                                    onClick={(e) => {
                                        e.stopPropagation();
                                        navigate(`/quiz/${quiz.id}`);
                                    }}
                                >
                                    Take Quiz
                                </Button>
                            </Card.Footer>
                        </Card>
                    </Col>
                ))}
            </Row>
        </Container>
    );
};

export default QuizListPage; 