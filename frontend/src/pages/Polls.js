//setup
//useState enables functional components to have their own memory for data
import React, { useState } from "react";

function PollPage() {
const [polls, setPolls] = useState([]);
const [nextPollId, setNextPollId] = useState(1);
const [nextOptionId, setNextOptionId] = useState(1);


//add Poll Function

const addPoll = () => {
    setPolls([...polls,
      { id: nextPollId, title: "", options: [], newOptionName: "" },
    ]);
    setNextPollId(nextPollId + 1);
  };

  //Update Poll titlee
 const updatePollTitle = (pollId, newTitle) => {
    setPolls(polls.map((poll) => poll.id === pollId ? { ...poll, title: newTitle } : poll
      )
    );
  };

//Typing in the option input 
//LOOK
 const namePoll = (pollId, name) => {
    setPolls(polls.map((poll) =>
        poll.id === pollId ? { ...poll, newOptionName: name } : poll
      )
    );
  };
//react cant handle updating ui if thigns are moved by place
const addOption = (pollId) => {
    setPolls(
      polls.map((poll) => {
        if (poll.id === pollId && poll.newOptionName.trim() !== "") {
          return {
            ...poll,
            options: [
              ...poll.options,
              { id: nextOptionId, name: poll.newOptionName, votes: 0 },
            ],
            newOptionName: "",
          };
        }
        return poll;
      })
    );
    setNextOptionId(nextOptionId + 1);
  };



//Voting
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

// All of the Styling

return (
    <div style={{ padding: "20px" }}>
      <h1>Polls </h1>
      <p className="lead mb-4">
        Let members cast votes on event details.       </p>
      <button onClick={addPoll} className="addpoll-button">+ Add Poll</button>

      <div style={{display: "flex", flexWrap: "wrap", gap: "20px", marginTop: "20px"}} >
      {polls.map((poll) => (
        <div
          key={poll.id}
          className="poll-card"
        >
          {/* Poll title */}
          <input
            value={poll.title}
            onChange={(element) => updatePollTitle(poll.id, element.target.value)}
            placeholder="Insert Poll Title"
            style={{ fontSize: "1.2em", display: "block", width: "100%", marginBottom: "5px" }}
          />

          {/* List of options */}
          <ul style={{ listStyle: "none", paddingLeft: 0}}>
            {poll.options.map((option) => (
              <li key={option.id} 
              style={{ display: "flex", marginBottom: "5px", justifyContent: "space-between", alignItems: "center" }}>
                {/* Option name */}
              <span>{option.name}</span>

              {/* Right-aligned votes + button */}
              <span style={{ display: "flex", gap: "10px", alignItems: "center" }}>
                <span>{option.votes} Votes</span>
                <button onClick={() => vote(poll.id, option.id)}>Vote</button>
              </span>
              </li>
            ))}
          </ul>
          
          {/* Input to add a new option */}
          <input
            type="text"
            placeholder="Insert New Option"
            value={poll.newOptionName || ""}
            onChange={(e) => namePoll(poll.id, e.target.value)}
            style={{ marginRight: "5px" }}
           />
          <button onClick={() => addOption(poll.id)}
            className="option-button"
            >
            + 
          </button>
        </div>
      ))}
    </div>
    </div>
  );

}

export default PollPage;
