import React, { useState } from "react";
import { Form, Button, Card, ListGroup, Row, Col } from "react-bootstrap";

function PollPage() {
  const [polls, setPolls] = useState([]);
  const [nextPollId, setNextPollId] = useState(1);
  const [nextOptionId, setNextOptionId] = useState(1);

  const addPoll = () => {
    const newPoll = { id: nextPollId, title: "", options: [], newOptionName: "" };
    setPolls([...polls, newPoll]);
    setNextPollId(nextPollId + 1);
  };

  const updatePollTitle = (pollId, newTitle) => {
    setPolls(
      polls.map((poll) => (poll.id === pollId ? { ...poll, title: newTitle } : poll))
    );
  };

  const updateNewOptionName = (pollId, name) => {
    setPolls(
      polls.map((poll) => (poll.id === pollId ? { ...poll, newOptionName: name } : poll))
    );
  };

  const addOption = (pollId) => {
    setPolls(
      polls.map((poll) => {
        if (poll.id === pollId && poll.newOptionName.trim() !== "") {
          const newOption = { id: nextOptionId, name: poll.newOptionName, votes: 0 };
          setNextOptionId(nextOptionId + 1);
          return { ...poll, options: [...poll.options, newOption], newOptionName: "" };
        }
        return poll;
      })
    );
  };

  const vote = (pollId, optionId) => {
    setPolls(
      polls.map((poll) => {
        if (poll.id === pollId) {
          return {
            ...poll,
            options: poll.options.map((opt) =>
              opt.id === optionId ? { ...opt, votes: opt.votes + 1 } : opt
            ),
          };
        }
        return poll;
      })
    );
  };

  return (
    <div className="poll-page" style={{ padding: "20px" }}>
      <p className="lead mb-4">Let members cast votes on event details.</p>

      <Button className="addpoll-button mb-3" onClick={addPoll}>
        + Add Poll
      </Button>

      {polls.length === 0 && <p>No polls available yet.</p>}

      <Row className="g-3">
        {polls.map((poll) => (
          <Col key={poll.id} xs={12} sm={6} md={4} lg={3}>
            <Card className="shadow-sm">
              <Card.Body>
                {/* Poll Title */}
                <Form.Group className="mb-3" controlId={`pollTitle${poll.id}`}>
                  <Form.Control
                    type="text"
                    placeholder="Insert Poll Title"
                    value={poll.title}
                    onChange={(e) => updatePollTitle(poll.id, e.target.value)}
                  />
                </Form.Group>

                {/* Poll Options */}
                <ListGroup className="mb-3">
                  {poll.options.map((option) => (
                    <ListGroup.Item
                      key={option.id}
                      className="d-flex justify-content-between align-items-center"
                    >
                      <span>{option.name}</span>
                      <div className="d-flex align-items-center gap-2">
                        <span>{option.votes} Votes</span>
                        <Button size="sm" onClick={() => vote(poll.id, option.id)}>
                          Vote
                        </Button>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>

                {/* Add New Option */}
                <Form
                  onSubmit={(e) => {
                    e.preventDefault();
                    addOption(poll.id);
                  }}
                  className="d-flex"
                >
                  <Form.Group className="flex-grow-1 me-2" controlId={`pollOption${poll.id}`}>
                    <Form.Control
                      type="text"
                      placeholder="Enter your option"
                      value={poll.newOptionName || ""}
                      onChange={(e) => updateNewOptionName(poll.id, e.target.value)}
                      required
                    />
                  </Form.Group>
                  <Button type="submit" className="option-button">
                    +
                  </Button>
                </Form>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </div>
  );
}

export default PollPage;
