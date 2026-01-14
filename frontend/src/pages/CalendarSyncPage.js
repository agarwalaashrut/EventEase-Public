// src/pages/CalendarSyncPage.js
import React, { useState, useEffect } from "react";
import { Container, Card, Button, Alert, Spinner, Badge, ListGroup, Form } from "react-bootstrap";
import api from "../services/api";

function CalendarSyncPage() {
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(false);
  const [conflicts, setConflicts] = useState([]);
  const [error, setError] = useState(null);
  const [userEmail, setUserEmail] = useState("");
  const [emailInput, setEmailInput] = useState("");
  const [pageLoading, setPageLoading] = useState(true);

  // Get user email from localStorage or URL params
  useEffect(() => {
    const getUserEmail = async () => {
      try {
        // Try to get from localStorage
        let email = localStorage.getItem('userEmail');
        
        // Try to get from URL params (after OAuth callback)
        if (!email) {
          const params = new URLSearchParams(window.location.search);
          email = params.get('email');
          if (email) {
            localStorage.setItem('userEmail', email);
          }
        }
        
        if (email) {
          setUserEmail(email);
          setEmailInput(email);
          // Check calendar status
          try {
            const res = await api.calendar.status(email);
            if (res.success && res.calendar_connected) {
              setConnected(true);
              fetchConflicts(email);
            }
          } catch (err) {
            console.error("Error checking calendar status:", err);
          }
        }
      } catch (err) {
        console.error("Error getting user email:", err);
      } finally {
        setPageLoading(false);
      }
    };
    
    getUserEmail();
  }, []);

  const connectCalendar = async () => {
    if (!emailInput.trim()) {
      setError("Please enter your email address.");
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      // Store the email for future use
      localStorage.setItem('userEmail', emailInput);
      setUserEmail(emailInput);
      
      // Get the OAuth URL from backend
      const res = await api.calendar.connect();
      if (res.success && res.auth_url) {
        // Redirect to Google OAuth
        window.location.href = res.auth_url;
      } else {
        setError(res.error || "Failed to initiate calendar connection.");
      }
    } catch (err) {
      console.error("Error connecting to calendar:", err);
      setError("Error connecting to calendar.");
    } finally {
      setLoading(false);
    }
  };

  const fetchConflicts = async (email = userEmail) => {
    if (!email) return;
    try {
      const res = await api.calendar.getConflicts(email);
      if (res.success) {
        setConflicts(res.conflicts || []);
      }
    } catch (err) {
      console.error("Error fetching conflicts:", err);
    }
  };

  const disconnectCalendar = async () => {
    if (!userEmail) {
      setError("User email not found.");
      return;
    }
    
    setLoading(true);
    setError(null);
    try {
      const res = await api.calendar.disconnect(userEmail);
      if (res.success) {
        setConnected(false);
        setConflicts([]);
      } else {
        setError(res.error || "Failed to disconnect calendar.");
      }
    } catch (err) {
      console.error("Error disconnecting calendar:", err);
      setError("Error disconnecting calendar.");
    } finally {
      setLoading(false);
    }
  };

  if (pageLoading) {
    return (
      <Container className="py-4 text-center">
        <Spinner animation="border" role="status">
          <span className="visually-hidden">Loading...</span>
        </Spinner>
      </Container>
    );
  }

  return (
    <Container className="py-4">
      <h1 className="mb-4">Sync Your Calendar</h1>

      {error && <Alert variant="danger">{error}</Alert>}

      <Card className="shadow-sm mb-4">
        <Card.Body>
          {!connected ? (
            <>
              <p>Connect your Google Calendar to automatically sync your scheduled events.</p>
              
              {!userEmail && (
                <Form.Group className="mb-3">
                  <Form.Label>Email Address</Form.Label>
                  <Form.Control
                    type="email"
                    placeholder="Enter your email"
                    value={emailInput}
                    onChange={(e) => setEmailInput(e.target.value)}
                    disabled={loading}
                  />
                  <Form.Text className="text-muted">
                    We'll use this to connect your Google Calendar.
                  </Form.Text>
                </Form.Group>
              )}
              
              <Button 
                onClick={connectCalendar} 
                disabled={loading || !emailInput.trim()}
              >
                {loading ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Connecting...
                  </>
                ) : (
                  "Connect Google Calendar"
                )}
              </Button>
            </>
          ) : (
            <>
              <Alert variant="success">
                ✅ Calendar connected for <strong>{userEmail}</strong>
              </Alert>
              <Button 
                variant="outline-danger" 
                onClick={disconnectCalendar}
                disabled={loading}
              >
                {loading ? (
                  <>
                    <Spinner animation="border" size="sm" className="me-2" />
                    Disconnecting...
                  </>
                ) : (
                  "Disconnect Calendar"
                )}
              </Button>
            </>
          )}
        </Card.Body>
      </Card>

      {connected && (
        <Card>
          <Card.Body>
            <h5>Detected Conflicts</h5>
            {conflicts.length === 0 ? (
              <p className="text-muted">No conflicts found.</p>
            ) : (
              <ListGroup>
                {conflicts.map((slot, i) => (
                  <ListGroup.Item key={i}>
                    <div className="d-flex justify-content-between align-items-center">
                      <span>{slot.title} — {new Date(slot.time).toLocaleString()}</span>
                      <Badge bg="danger">Conflict</Badge>
                    </div>
                  </ListGroup.Item>
                ))}
              </ListGroup>
            )}
          </Card.Body>
        </Card>
      )}
    </Container>
  );
}

export default CalendarSyncPage;
