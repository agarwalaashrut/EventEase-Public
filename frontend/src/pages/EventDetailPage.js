import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Container, Row, Col, Card, Badge, Button, Spinner, Alert, Form } from 'react-bootstrap';
import api from '../services/api';

function EventDetailPage() {
  const { eventId } = useParams();
  const navigate = useNavigate();
  const [event, setEvent] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [suggestions, setSuggestions] = useState([]);
  const [dateMMDD, setDateMMDD] = useState('');
  const [timeHHMM, setTimeHHMM] = useState('');
  const [suggestedLocation, setSuggestedLocation] = useState('');

  useEffect(() => {
    fetchEventDetails();
  }, [eventId]);

  const fetchEventDetails = async () => {
    try {
      setLoading(true);
      const response = await api.events.getById(eventId);
      if (response.success) {
        setEvent(response.event);
      } else {
        setError(response.error || 'Failed to fetch event details');
      }
    } catch (err) {
      setError('Error connecting to server');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  if (loading) {
    return (
      <Container className="mt-5 text-center">
        <Spinner animation="border" />
        <p className="mt-3">Loading event details...</p>
      </Container>
    );
  }

  if (error) {
    return (
      <Container className="mt-5">
        <Alert variant="danger">{error}</Alert>
        <Button variant="secondary" onClick={() => navigate('/events')}>
          Back to Events
        </Button>
      </Container>
    );
  }

  if (!event) {
    return (
      <Container className="mt-5">
        <Alert variant="warning">Event not found</Alert>
        <Button variant="secondary" onClick={() => navigate('/events')}>
          Back to Events
        </Button>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <Button variant="outline-secondary" onClick={() => navigate('/events')} className="mb-4">
        ← Back to Events
      </Button>

      <Card className="shadow-sm">
        <Card.Body>
          <div className="d-flex justify-content-between align-items-start mb-4">
            <div>
              <h1 className="mb-2">{event.title}</h1>
              <Badge bg={event.status === 'confirmed' ? 'success' : 'warning'}>
                {event.status}
              </Badge>
            </div>
          </div>

          <Row>
            <Col md={8}>
              <h5>Description</h5>
              <p className="mb-4">{event.description}</p>

              <h5>Location</h5>
              <p className="mb-4">{event.location}</p>

              <h5>Organizer</h5>
              <p>{event.organizer}</p>
              <p className="text-muted mb-4">{event.organizer_email}</p>

              <h5>Proposed Times</h5>
              {event.proposed_times && event.proposed_times.length > 0 ? (
                <ul className="list-unstyled">
                  {event.proposed_times.map((time, idx) => (
                    <li key={idx} className="mb-2">
                      {formatDate(time)}
                    </li>
                  ))}
                </ul>
              ) : (
                <p className="text-muted">No times proposed yet</p>
              )}

              <hr />
              <h5 className="mt-4">Suggest a Time or Location</h5>
              <Form
                onSubmit={(e) => {
                  e.preventDefault();
                  if (!dateMMDD && !timeHHMM && !suggestedLocation) return;
                  const combined = dateMMDD && timeHHMM ? `${dateMMDD} ${timeHHMM}` : (dateMMDD || timeHHMM || null);
                  const newSuggestion = {
                    time: combined,
                    location: suggestedLocation || null
                  };
                  setSuggestions([...suggestions, newSuggestion]);
                  setDateMMDD('');
                  setTimeHHMM('');
                  setSuggestedLocation('');
                }}
              >
                <Row className="g-2 align-items-end">
                  <Col md={4}>
                    <Form.Group controlId="dateMMDD">
                      <Form.Label>Date (MM/DD)</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="e.g., 11/08"
                        value={dateMMDD}
                        onChange={(e) => setDateMMDD(e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group controlId="timeHHMM">
                      <Form.Label>Time</Form.Label>
                      <Form.Control
                        type="time"
                        value={timeHHMM}
                        onChange={(e) => setTimeHHMM(e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={4}>
                    <Form.Group controlId="suggestedLocation">
                      <Form.Label>Suggested Location</Form.Label>
                      <Form.Control
                        type="text"
                        placeholder="Enter a location"
                        value={suggestedLocation}
                        onChange={(e) => setSuggestedLocation(e.target.value)}
                      />
                    </Form.Group>
                  </Col>
                </Row>
                <Button type="submit" variant="primary" className="mt-3">
                  Add Suggestion
                </Button>
              </Form>

              {suggestions.length > 0 && (
                <>
                  <h6 className="mt-4">Your Suggestions</h6>
                  <ul className="list-unstyled">
                    {suggestions.map((s, idx) => (
                      <li key={idx} className="mb-2">
                        {s.time && <div>Time: {s.time}</div>}
                        {s.location && <div>Location: {s.location}</div>}
                      </li>
                    ))}
                  </ul>
                </>
              )}
            </Col>

            <Col md={4}>
              <Card className="mb-4">
                <Card.Body>
                  <h5>Attendees ({event.attendees?.length || 0})</h5>
                  {event.attendees && event.attendees.length > 0 ? (
                    <ul className="list-unstyled">
                      {event.attendees.map((attendee, idx) => (
                        <li key={idx} className="mb-2">
                          {attendee}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-muted">No attendees yet</p>
                  )}
                </Card.Body>
              </Card>

              <Card>
                <Card.Body>
                  <h5 className="mb-3">Event Details</h5>
                  <p className="mb-2">
                    <strong>Created:</strong> {formatDate(event.created_at)}
                  </p>
                  <p className="mb-0">
                    <strong>Status:</strong> {event.status}
                  </p>
                </Card.Body>
              </Card>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default EventDetailPage;
