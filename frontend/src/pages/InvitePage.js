import React, { useState } from 'react';
import { Container, Card, Form, Button, ListGroup } from 'react-bootstrap';

function InvitePage({ eventId }) {
  const [email, setEmail] = useState('');
  const [invitees, setInvitees] = useState([]);

  //adding email function
  const AddInvite = (e) => {
    e.preventDefault();
    //remove spaces from email
    const trimmedEmail = email.trim();
    if (!trimmedEmail) return;

    if (!invitees.includes(trimmedEmail)) {
      setInvitees([...invitees, trimmedEmail]);
    }

    setEmail('');
  };

  return (
    
      <Card className="shadow-sm mb-4">
        <Card.Body>
          <h5 className="mb-4">Invite People to Event</h5>

          <Form onSubmit={AddInvite}>
            <Form.Group className="mb-3" controlId="inviteEmail">
              <Form.Label>Email Address</Form.Label>
              <Form.Control
                type="email"
                placeholder="Enter email to invite"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
              />
            </Form.Group>

            <Button type="submit" variant="primary">
              Add to Invite List
            </Button>
          </Form>

          {invitees.length > 0 && (
            <div className="mt-4">
              <h5>Invite List</h5>
              <ListGroup>
                {invitees.map((e, idx) => (
                  <ListGroup.Item key={idx}>{e}</ListGroup.Item>
                ))}
              </ListGroup>
            </div>
          )}
        </Card.Body>
      </Card>
   
  );
}

export default InvitePage;
