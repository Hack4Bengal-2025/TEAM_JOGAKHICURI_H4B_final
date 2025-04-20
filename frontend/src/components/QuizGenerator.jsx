import React, { useState } from 'react';

const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
const [isExpanded, setIsExpanded] = useState(false);

{/* Question Grid */}
<div className="col-md-3">
    <div className="question-grid">
        <div className="grid-header">
            <h5>All Questions</h5>
            <button 
                className="show-all-btn"
                onClick={() => setIsExpanded(!isExpanded)}
            >
                {isExpanded ? 'Show Less' : 'Show All'}
            </button>
        </div>
        <div className={`grid-buttons ${isExpanded ? 'expanded' : ''}`}>
            {questions.map((_, index) => (
                <button
                    key={index}
                    className={`grid-button ${index === currentQuestionIndex ? 'active' : ''} ${
                        answers[index] !== undefined ? 'answered' : 'unanswered'
                    }`}
                    onClick={() => setCurrentQuestionIndex(index)}
                >
                    {index + 1}
                </button>
            ))}
        </div>
    </div>
</div> 