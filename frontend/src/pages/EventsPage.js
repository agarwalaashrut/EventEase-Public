import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Button, Container, Row, Col, Badge, Spinner, Alert} from 'react-bootstrap';
import api from '../services/api';
import PollsPage from './Polls';

function EventsPage() {
  const navigate = useNavigate();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showPolls, setShowPolls] = useState(false);
  

  useEffect(() => {
    fetchEvents();
  }, []);

  const fetchEvents = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await api.events.getAll();

      if (response.success) {
        setEvents(response.events || []);
      } else {
        setError(response.error || 'Failed to fetch events');
      }
    } catch (err) {
      setError('Unable to connect to server. Make sure the backend is running.');
      console.error('Error fetching events:', err);
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (showPolls) {
    return (
      <Container className="py-4">
        <Button variant="primary" onClick={() => setShowPolls(false)} className="mb-3">
          Back to Events
        </Button>
        <PollsPage />
      </Container>
    );
  }
  if (loading) {
    return (
      <Container className="text-center mt-5">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
        <p className="mt-3">Loading events...</p>
      </Container>
    );
  }

  return (
    <Container className="events-page py-4">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h1>My Events</h1>
        <Button variant="primary" size="lg" onClick={() => setShowPolls(true)}>
        <Button variant="primary" size="lg" onClick={() => navigate('/events/create')}>
          + Create New Event
        </Button>
      </div>

      {error && (
        <Alert variant="danger" dismissible onClose={() => setError(null)}>
          {error}
        </Alert>
      )}

      {events.length === 0 ? (
        <Card className="mt-4">
          <Card.Body className="text-center py-5">
            <Card.Title>No events yet</Card.Title>
            <Card.Text className="text-muted mb-4">
              Create your first event to get started!
            </Card.Text>
            <Button variant="primary" size="lg" onClick={() => navigate('/events/create')}>
              Create New Event
            </Button>
          </Card.Body>
        </Card>
      ) : (
        <Row>
          {events.map((event) => (
            <Col key={event._id} md={6} lg={4} className="mb-4">
              <Card className="h-100 shadow-sm">
                <Card.Body>
                  <div className="d-flex justify-content-between align-items-start mb-2">
                    <Card.Title>{event.title}</Card.Title>
                    <Badge
                      bg={event.status === 'confirmed' ? 'success' : 'warning'}
                      className="ms-2"
                    >
                      {event.status}
                    </Badge>
                  </div>

                  <Card.Text className="text-muted small mb-3">
                    {event.description}
                  </Card.Text>

                  <div className="mb-2">
                    <strong> Location:</strong> {event.location}
                  </div>

                  <div className="mb-2">
                    <strong> Organizer:</strong> {event.organizer}
                  </div>

                  <div className="mb-3">
                    <strong> Attendees:</strong> {event.attendees?.length || 0}
                  </div>

                  {event.proposed_times && event.proposed_times.length > 0 && (
                    <div className="mb-3">
                      <strong> Proposed Times:</strong>
                      <ul className="small mt-1 ps-3">
                        {event.proposed_times.slice(0, 2).map((time, idx) => (
                          <li key={idx}>{formatDate(time.start)}</li>
                        ))}
                        {event.proposed_times.length > 2 && (
                          <li className="text-muted">
                            +{event.proposed_times.length - 2} more
                          </li>
                        )}
                      </ul>
                    </div>
                  )}

                  <div className="d-grid gap-2">
                    <Button
                      variant="outline-primary"
                      size="sm"
                      onClick={() => navigate(`/events/${event._id}`)}
                    >
                      View Details
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      )}
    </Container>
  );
}

export default EventsPage;
