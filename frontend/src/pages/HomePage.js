import React from 'react';
import { Card, Button, Row, Col } from 'react-bootstrap';

function HomePage() {
  return (
    <div className="home-page">
      <h1 className="mb-4">Welcome to EventEase</h1>
      <p className="lead mb-4">
        Plan events, suggest times and locations, vote on preferences, and sync to Google Calendar.
      </p>
      
      <Row>
        <Col md={4} className="mb-3">
          <Card className="event-card h-100">
            <Card.Body>
              <Card.Title>Create Events</Card.Title>
              <Card.Text>
                Easily create and manage your events with our intuitive interface.
              </Card.Text>
              <Button variant="primary">Get Started</Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4} className="mb-3">
          <Card className="event-card h-100">
            <Card.Body>
              <Card.Title>Collaborate</Card.Title>
              <Card.Text>
                Suggest times and locations, and let everyone vote on their preferences.
              </Card.Text>
              <Button variant="primary">Learn More</Button>
            </Card.Body>
          </Card>
        </Col>
        
        <Col md={4} className="mb-3">
          <Card className="event-card h-100">
            <Card.Body>
              <Card.Title>Sync Calendar</Card.Title>
              <Card.Text>
                Automatically sync finalized events to your Google Calendar.
              </Card.Text>
              <Button variant="primary">Connect</Button>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </div>
  );
}

export default HomePage;
