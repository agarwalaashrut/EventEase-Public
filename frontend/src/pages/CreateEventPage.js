import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Container, Card, Form, Button, Alert, Row, Col } from 'react-bootstrap';
import api from '../services/api';

function CreateEventPage() {
  const navigate = useNavigate();

  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [location, setLocation] = useState('');
  const [organizer, setOrganizer] = useState('');
  const [organizerEmail, setOrganizerEmail] = useState('');
  const [startDateTime, setStartDateTime] = useState('');
  const [endDateTime, setEndDateTime] = useState('');

  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    if (!title || !description || !organizer || !organizerEmail) {
      setError('Title, description, organizer, and organizer email are required.');
      return;
    }

    try {
      setLoading(true);

      const payload = {
        title,
        description,
        location,
        organizer,
        organizer_email: organizerEmail
      };

      if (startDateTime || endDateTime) {
        payload.time_range = {
          start: startDateTime ? new Date(startDateTime).toISOString() : null,
          end: endDateTime ? new Date(endDateTime).toISOString() : null
        };
      }

      const response = await api.events.create(payload);

      if (response.success) {
        // If your API returns the created event with _id, you can navigate to its detail page:
        // navigate(`/events/${response.event._id}`);
        navigate('/events');
      } else {
        setError(response.error || 'Failed to create event.');
      }
    } catch {
      setError('Error connecting to server.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="py-4">
      <Button variant="outline-secondary" onClick={() => navigate('/events')} className="mb-4">
        ← Back to Events
      </Button>

      <Card className="shadow-sm p-4">
        <h2 className="mb-4">Create New Event</h2>

        {error && <Alert variant="danger">{error}</Alert>}

        <Form onSubmit={handleSubmit}>
          <Form.Group className="mb-3">
            <Form.Label>Title</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter event title"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Description</Form.Label>
            <Form.Control
              as="textarea"
              rows={3}
              placeholder="Enter event description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              required
            />
          </Form.Group>

          <Form.Group className="mb-3">
            <Form.Label>Location</Form.Label>
            <Form.Control
              type="text"
              placeholder="Enter event location"
              value={location}
              onChange={(e) => setLocation(e.target.value)}
            />
          </Form.Group>

          <Row className="g-3">
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Organizer</Form.Label>
                <Form.Control
                  type="text"
                  placeholder="Enter organizer name"
                  value={organizer}
                  onChange={(e) => setOrganizer(e.target.value)}
                  required
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group className="mb-3">
                <Form.Label>Organizer Email</Form.Label>
                <Form.Control
                  type="email"
                  placeholder="name@example.com"
                  value={organizerEmail}
                  onChange={(e) => setOrganizerEmail(e.target.value)}
                  required
                />
              </Form.Group>
            </Col>
          </Row>

          <div className="mb-2 fw-semibold">Optional Time Range</div>
          <Row className="g-3">
            <Col md={6}>
              <Form.Group>
                <Form.Label>Start</Form.Label>
                <Form.Control
                  type="datetime-local"
                  value={startDateTime}
                  onChange={(e) => setStartDateTime(e.target.value)}
                />
              </Form.Group>
            </Col>
            <Col md={6}>
              <Form.Group>
                <Form.Label>End</Form.Label>
                <Form.Control
                  type="datetime-local"
                  value={endDateTime}
                  onChange={(e) => setEndDateTime(e.target.value)}
                />
              </Form.Group>
            </Col>
          </Row>

          <Button type="submit" variant="primary" className="mt-3" disabled={loading}>
            {loading ? 'Creating...' : 'Create Event'}
          </Button>
        </Form>
      </Card>
    </Container>
  );
}

export default CreateEventPage;
