import React, { useState, useEffect } from 'react';
import { Container, Row, Col, Card, Badge, Button, ProgressBar } from 'react-bootstrap';
import { useLocation, useNavigate, useParams } from 'react-router-dom';
import { FaArrowLeft, FaCheck, FaTimes, FaRegClock, FaTrophy, FaChartBar } from 'react-icons/fa';
import '../styles/QuizAnalysis.css';

const QuizAnalysis = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { id: quizId } = useParams();
    const [quizData, setQuizData] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        if (location.state?.quiz && location.state?.selectedAnswers) {
            setQuizData({
                quiz: location.state.quiz,
                selectedAnswers: location.state.selectedAnswers,
                timeSpent: location.state.timeSpent || 0,
                quizStartTime: location.state.quizStartTime,
                quizEndTime: location.state.quizEndTime
            });
        } else {
            // If no state is passed, redirect back to quizzes
            navigate('/quizzes');
        }
        setLoading(false);
    }, [location, navigate]);

    const calculateScore = () => {
        if (!quizData) return { score: 0, total: 0, percentage: 0 };

        let score = 0;
        const questions = quizData.quiz.questions;
        const answers = quizData.selectedAnswers;

        questions.forEach((question, index) => {
            if (answers[index] === question.answer) {
                score++;
            }
        });

        return {
            score,
            total: questions.length,
            percentage: Math.round((score / questions.length) * 100)
        };
    };

    const formatTime = (seconds) => {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = seconds % 60;
        return `${minutes}:${remainingSeconds < 10 ? '0' : ''}${remainingSeconds}`;
    };

    const getPerformanceCategory = (percentage) => {
        if (percentage >= 90) return { label: 'Excellent', color: 'success' };
        if (percentage >= 70) return { label: 'Good', color: 'primary' };
        if (percentage >= 50) return { label: 'Average', color: 'warning' };
        return { label: 'Needs Improvement', color: 'danger' };
    };

    const countAnsweredQuestions = () => {
        if (!quizData) return 0;
        return Object.keys(quizData.selectedAnswers).length;
    };

    const countUnansweredQuestions = () => {
        if (!quizData) return 0;
        return quizData.quiz.questions.length - countAnsweredQuestions();
    };

    if (loading || !quizData) {
        return (
            <Container className="quiz-analysis-container py-5">
                <div className="text-center my-5">
                    <h2>Loading analysis...</h2>
                </div>
            </Container>
        );
    }

    const score = calculateScore();
    const performance = getPerformanceCategory(score.percentage);

    return (
        <Container className="quiz-analysis-container">
            <Row className="mb-4 align-items-center">
                <Col>
                    <Button
                        variant="outline-primary"
                        className="back-button rounded-pill me-3"
                        onClick={() => navigate('/quizzes')}
                    >
                        <FaArrowLeft className="me-2" />
                        Back to Quizzes
                    </Button>
                    <h1 className="d-inline fw-bold">Quiz Analysis</h1>
                </Col>
            </Row>

            <Row>
                <Col lg={4}>
                    <div className="d-flex flex-column gap-3">
                        <Card className="score-summary-card">
                            <Card.Body className="text-center">
                                <h3 className="mb-3">Score Summary</h3>
                                <div className="score-circle" style={{ "--percentage": `${score.percentage}%` }}>
                                    <div className="score-percentage">{score.percentage}%</div>
                                </div>
                                <h5 className="mt-2">
                                    <Badge bg={performance.color}>{performance.label}</Badge>
                                </h5>
                                <p className="text-muted mb-2">
                                    {score.score} out of {score.total} correct
                                </p>
                                <div className="d-flex justify-content-between">
                                    <span>Time Spent</span>
                                    <span className="fw-bold">
                                        <FaRegClock className="me-1" />
                                        {formatTime(quizData.timeSpent)}
                                    </span>
                                </div>
                                <div className="d-flex justify-content-between">
                                    <span>Attempted</span>
                                    <span className="fw-bold">{countAnsweredQuestions()}/{quizData.quiz.questions.length}</span>
                                </div>
                            </Card.Body>
                        </Card>

                        <Card className="performance-card">
                            <Card.Body>
                                <h4 className="mb-3">Performance</h4>
                                <div className="performance-stats">
                                    <div className="performance-stat-item">
                                        <span>Correct</span>
                                        <span className="fw-bold text-success">{score.score}</span>
                                    </div>
                                    <ProgressBar
                                        variant="success"
                                        now={(score.score / score.total) * 100}
                                        className="mb-2"
                                    />

                                    <div className="performance-stat-item">
                                        <span>Incorrect</span>
                                        <span className="fw-bold text-danger">{score.total - score.score}</span>
                                    </div>
                                    <ProgressBar
                                        variant="danger"
                                        now={((score.total - score.score) / score.total) * 100}
                                        className="mb-2"
                                    />

                                    <div className="performance-stat-item">
                                        <span>Unanswered</span>
                                        <span className="fw-bold text-secondary">{countUnansweredQuestions()}</span>
                                    </div>
                                    <ProgressBar
                                        variant="secondary"
                                        now={(countUnansweredQuestions() / score.total) * 100}
                                    />
                                </div>
                            </Card.Body>
                        </Card>
                    </div>
                </Col>

                <Col lg={8}>
                    <Card className="question-analysis-card">
                        <Card.Body>
                            <h3 className="mb-4">
                                <FaChartBar className="me-2" />
                                Detailed Analysis
                            </h3>

                            {quizData.quiz.questions.map((question, index) => {
                                const userAnswer = quizData.selectedAnswers[index];
                                const isCorrect = userAnswer === question.answer;
                                const hasAnswered = userAnswer !== undefined;

                                return (
                                    <Card
                                        key={index}
                                        className={`question-review-item ${isCorrect ? 'correct' : hasAnswered ? 'incorrect' : 'unanswered'}`}
                                    >
                                        <Card.Body>
                                            <div className="d-flex justify-content-between mb-2">
                                                <h5>Question {index + 1}</h5>
                                                {hasAnswered ? (
                                                    isCorrect ? (
                                                        <Badge bg="success" className="status-badge">
                                                            <FaCheck /> Correct
                                                        </Badge>
                                                    ) : (
                                                        <Badge bg="danger" className="status-badge">
                                                            <FaTimes /> Incorrect
                                                        </Badge>
                                                    )
                                                ) : (
                                                    <Badge bg="secondary" className="status-badge">
                                                        Unanswered
                                                    </Badge>
                                                )}
                                            </div>

                                            <p className="question-text">{question.question}</p>

                                            <div className="options-list">
                                                {question.options.map((option, optIndex) => {
                                                    let optionClass = '';
                                                    if (option === question.answer) {
                                                        optionClass = 'correct-answer';
                                                    } else if (option === userAnswer) {
                                                        optionClass = 'incorrect-answer';
                                                    }

                                                    return (
                                                        <div key={optIndex} className={`option-item ${optionClass}`}>
                                                            {option}
                                                            {option === question.answer && (
                                                                <FaCheck className="answer-icon correct" />
                                                            )}
                                                            {option === userAnswer && option !== question.answer && (
                                                                <FaTimes className="answer-icon incorrect" />
                                                            )}
                                                        </div>
                                                    );
                                                })}
                                            </div>
                                        </Card.Body>
                                    </Card>
                                );
                            })}
                        </Card.Body>
                    </Card>
                </Col>
            </Row>

            <div className="d-flex justify-content-center mt-4 mb-5">
                <Button
                    variant="primary"
                    className="action-button me-3"
                    onClick={() => navigate(`/quiz/${quizId}`)}
                >
                    <FaTrophy className="me-2" />
                    Retry Quiz
                </Button>
                <Button
                    variant="outline-primary"
                    className="action-button"
                    onClick={() => navigate('/quizzes')}
                >
                    Back to Quizzes
                </Button>
            </div>
        </Container>
    );
};

export default QuizAnalysis; 