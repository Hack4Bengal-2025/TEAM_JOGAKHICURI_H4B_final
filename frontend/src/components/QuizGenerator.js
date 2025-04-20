import React, { useState, useEffect } from 'react';
import { Container, Form, Button, Alert, Spinner, Card, Row, Col, Badge } from 'react-bootstrap';
import { FaRobot, FaUpload, FaFilePdf, FaTimes, FaArrowLeft, FaCheck, FaRegClock } from 'react-icons/fa';
import axios from 'axios';
import { useNavigate, useParams } from 'react-router-dom';
import '../styles/QuizGenerator.css';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const QuizGenerator = () => {
    const navigate = useNavigate();
    const { id: quizId } = useParams();
    const [showAiSection, setShowAiSection] = useState(!quizId);
    const [userPrompt, setUserPrompt] = useState('');
    const [files, setFiles] = useState([]);
    const [isGenerating, setIsGenerating] = useState(false);
    const [generationError, setGenerationError] = useState('');
    const [quiz, setQuiz] = useState(null);
    const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
    const [selectedAnswers, setSelectedAnswers] = useState({});
    const [showResults, setShowResults] = useState(false);
    const [quizStartTime, setQuizStartTime] = useState(null);
    const [quizEndTime, setQuizEndTime] = useState(null);
    const [timeSpent, setTimeSpent] = useState(0);
    const [intervalId, setIntervalId] = useState(null);

    useEffect(() => {
        if (quizId) {
            fetchQuiz();
        }
    }, [quizId]);

    useEffect(() => {
        if (quiz && !quizStartTime && !showAiSection) {
            setQuizStartTime(new Date());
            const interval = setInterval(() => {
                setTimeSpent(prevTime => prevTime + 1);
            }, 1000);
            setIntervalId(interval);
        }

        return () => {
            if (intervalId) {
                clearInterval(intervalId);
            }
        };
    }, [quiz, quizStartTime, showAiSection]);

    const fetchQuiz = async () => {
        try {
            const token = localStorage.getItem('token');
            const response = await axios.get(`${API_URL}/quizzes/${quizId}/view`, {
                headers: { Authorization: token ? `Bearer ${token}` : '' }
            });
            if (response.data.success) {
                setQuiz(response.data.data);
                setShowAiSection(false);
            }
        } catch (error) {
            console.error('Error fetching quiz:', error);
            setGenerationError('Failed to fetch quiz. Please try again later.');
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

    const generateQuiz = async () => {
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

            for (let i = 0; i < files.length; i++) {
                formData.append('files', files[i]);
            }

            const response = await axios.post(
                `${API_URL}/quizzes/create`,
                formData,
                {
                    headers: {
                        Authorization: token ? `Bearer ${token}` : '',
                        'Content-Type': 'multipart/form-data'
                    }
                }
            );

            if (response.data && response.data.success) {
                navigate('/quizzes');
            } else {
                setGenerationError(response.data?.message || 'Failed to generate quiz');
            }
        } catch (error) {
            console.error('Error generating quiz:', error);
            setGenerationError(
                'An error occurred: ' + (error.response?.data?.message || error.message)
            );
        } finally {
            setIsGenerating(false);
        }
    };

    const handleAnswerSelect = (answer) => {
        setSelectedAnswers({
            ...selectedAnswers,
            [currentQuestionIndex]: answer
        });
    };

    const nextQuestion = () => {
        if (currentQuestionIndex < quiz.questions.length - 1) {
            setCurrentQuestionIndex(currentQuestionIndex + 1);
        } else {
            finishQuiz();
        }
    };

    const previousQuestion = () => {
        if (currentQuestionIndex > 0) {
            setCurrentQuestionIndex(currentQuestionIndex - 1);
        }
    };

    const goToQuestion = (index) => {
        setCurrentQuestionIndex(index);
    };

    const finishQuiz = () => {
        setQuizEndTime(new Date());
        if (intervalId) {
            clearInterval(intervalId);
        }
        navigate(`/quiz/${quizId}/analysis`, {
            state: {
                quiz,
                selectedAnswers,
                timeSpent,
                quizStartTime: quizStartTime?.toISOString(),
                quizEndTime: new Date().toISOString()
            }
        });
    };

    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    };

    const getQuestionStatus = (index) => {
        if (selectedAnswers[index]) {
            return 'answered';
        }
        return 'unanswered';
    };

    if (!quiz) {
        return (
            <Container className="quiz-generator-container py-4">
                <div className="quiz-header d-flex align-items-center gap-3 mb-4">
                    <Button
                        variant="outline-primary"
                        className="back-button rounded-pill"
                        onClick={() => navigate('/quizzes')}
                    >
                        <FaArrowLeft className="me-2" />
                        Back to Quizzes
                    </Button>
                    <h1 className="display-4 fw-bold text-primary mb-0">
                        Generate Quiz
                    </h1>
                </div>

                <div className="ai-section">
                    <div className="d-flex justify-content-between align-items-center mb-4">
                        <h5 className="mb-0">
                            <FaRobot className="me-2" />
                            Generate Quiz with AI
                        </h5>
                    </div>

                    <Form.Group className="mb-4">
                        <Form.Label>Enter your prompt</Form.Label>
                        <Form.Control
                            as="textarea"
                            rows={3}
                            value={userPrompt}
                            onChange={(e) => setUserPrompt(e.target.value)}
                            placeholder="Describe what kind of quiz you want to generate..."
                            className="mb-3"
                        />
                    </Form.Group>

                    <div className="file-drop-zone mb-4">
                        <input
                            type="file"
                            id="file-upload"
                            accept=".pdf"
                            onChange={handleFileChange}
                            style={{ display: 'none' }}
                            multiple
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
                        onClick={generateQuiz}
                        disabled={isGenerating || !userPrompt}
                        className="w-100"
                    >
                        {isGenerating ? (
                            <>
                                <Spinner as="span" animation="border" size="sm" className="me-2" />
                                Generating Quiz...
                            </>
                        ) : (
                            'Generate Quiz'
                        )}
                    </Button>

                    {generationError && (
                        <Alert variant="danger" className="mt-3">
                            {generationError}
                        </Alert>
                    )}
                </div>
            </Container>
        );
    }

    if (!quiz.questions || quiz.questions.length === 0) {
        return (
            <Container className="quiz-container py-4">
                <Alert variant="warning">
                    This quiz has no questions. Please try another quiz.
                </Alert>
                <Button
                    variant="primary"
                    onClick={() => navigate('/quizzes')}
                    className="mt-3"
                >
                    Back to Quizzes
                </Button>
            </Container>
        );
    }

    const currentQuestion = quiz.questions[currentQuestionIndex];

    return (
        <Container fluid className="quiz-container py-4">
            <Row className="quiz-header mb-4 align-items-center">
                <Col>
                    <Button
                        variant="outline-primary"
                        className="back-button rounded-pill me-3"
                        onClick={() => navigate('/quizzes')}
                    >
                        <FaArrowLeft className="me-2" />
                        Exit Quiz
                    </Button>
                    <span className="quiz-title h3">{quiz.title}</span>
                </Col>
                <Col xs="auto">
                    <div className="quiz-timer">
                        <FaRegClock className="me-2" />
                        Time: {formatTime(timeSpent)}
                    </div>
                </Col>
            </Row>

            <Row>
                <Col md={3}>
                    <div className="question-grid">
                        <div className="grid-header mb-3">
                            <h5>Questions</h5>
                            <div className="d-flex justify-content-between mb-2">
                                <div className="legend-item">
                                    <span className="legend-color answered"></span>
                                    <span>Answered</span>
                                </div>
                                <div className="legend-item">
                                    <span className="legend-color unanswered"></span>
                                    <span>Unanswered</span>
                                </div>
                            </div>
                        </div>
                        <div className="grid-buttons">
                            {quiz.questions.map((question, index) => (
                                <Button
                                    key={index}
                                    variant={currentQuestionIndex === index ? "primary" : "outline-primary"}
                                    className={`grid-button ${getQuestionStatus(index)}`}
                                    onClick={() => goToQuestion(index)}
                                >
                                    {index + 1}
                                </Button>
                            ))}
                        </div>
                        <Button
                            variant="success"
                            className="finish-quiz-btn mt-4 w-100"
                            onClick={finishQuiz}
                        >
                            Finish Quiz
                        </Button>
                    </div>
                </Col>
                <Col md={9}>
                    <Card className="question-card">
                        <Card.Body>
                            <div className="question-header d-flex justify-content-between align-items-center mb-4">
                                <Badge bg="primary" className="question-number-badge">
                                    Question {currentQuestionIndex + 1} of {quiz.questions.length}
                                </Badge>
                            </div>

                            <h4 className="question-text mb-4">{currentQuestion.question}</h4>

                            <div className="options-container mb-4">
                                {currentQuestion.options && currentQuestion.options.map((option, index) => (
                                    <Button
                                        key={index}
                                        variant={selectedAnswers[currentQuestionIndex] === option ? 'primary' : 'outline-primary'}
                                        className={`option-button w-100 mb-2 ${selectedAnswers[currentQuestionIndex] === option ? 'active' : ''}`}
                                        onClick={() => handleAnswerSelect(option)}
                                    >
                                        {option}
                                    </Button>
                                ))}
                            </div>

                            <div className="d-flex justify-content-between">
                                <Button
                                    variant="outline-primary"
                                    onClick={previousQuestion}
                                    disabled={currentQuestionIndex === 0}
                                >
                                    Previous
                                </Button>
                                <Button
                                    variant="primary"
                                    onClick={nextQuestion}
                                >
                                    {currentQuestionIndex === quiz.questions.length - 1 ? 'Finish' : 'Next'}
                                </Button>
                            </div>
                        </Card.Body>
                    </Card>
                </Col>
            </Row>
        </Container>
    );
};

export default QuizGenerator; 