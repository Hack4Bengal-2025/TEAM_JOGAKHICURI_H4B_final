import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import 'bootstrap/dist/css/bootstrap.min.css';
import './App.css';
import NotesListPage from './components/NotesListPage';
import NoteEditor from './components/NoteEditor';
import NoteViewPage from './components/NoteViewPage';
import QuizGenerator from './components/QuizGenerator';
import QuizListPage from './components/QuizListPage';
import QuizAnalysis from './components/QuizAnalysis';

function App() {
  return (
    <Router>
      <div className="App">
        <Routes>
          <Route path="/" element={<NotesListPage />} />
          <Route path="/new" element={<NoteEditor />} />
          <Route path="/notes/:id" element={<NoteViewPage />} />
          <Route path="/notes/:id/edit" element={<NoteEditor />} />
          <Route path="/quizzes" element={<QuizListPage />} />
          <Route path="/quiz/new" element={<QuizGenerator />} />
          <Route path="/quiz/:id" element={<QuizGenerator />} />
          <Route path="/quiz/:id/analysis" element={<QuizAnalysis />} />
          <Route path="*" element={<Navigate to="/" />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
