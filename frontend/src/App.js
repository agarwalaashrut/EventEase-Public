import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import NavigationBar from './components/NavigationBar';
import { HomePage, EventsPage, EventDetailPage, CreateEventPage } from './pages'; // ✅ add CreateEventPage
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <NavigationBar />
        <Container className="mt-4">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/events" element={<EventsPage />} />
            <Route path="/events/create" element={<CreateEventPage />} /> {/* ✅ add this line above :eventId */}
            <Route path="/events/:eventId" element={<EventDetailPage />} />
          </Routes>
        </Container>
      </div>
    </Router>
  );
}

export default App;
