import "./Beginner.css";
import React, { useState, useEffect } from "react";
import { ChevronRight, RotateCcw } from "lucide-react";

type Mode = "intro" | "learning" | "quiz" | "results";

const Beginner = () => {
  const [currentIndex, setCurrentIndex] = useState(0);
  const [mode, setMode] = useState<Mode>("intro");
  const [displayedText, setDisplayedText] = useState("");
  const [isTyping, setIsTyping] = useState(true);
  const [quizAnswers, setQuizAnswers] = useState<Record<number, string>>({});
  const [shownHints, setShownHints] = useState<Record<number, boolean>>({});

  const letters = [
    { letter: "A", instruction: "Make a fist with your thumb on the side", image: "✊" },
    { letter: "B", instruction: "Hold your hand flat with fingers together, thumb across palm", image: "🖐️" },
    { letter: "C", instruction: "Curve your hand to form a C shape", image: "🤌" },
    { letter: "D", instruction: "Point your index finger up, other fingers touch thumb", image: "☝️" },
    { letter: "E", instruction: "Curl all fingers down toward palm, thumb across them", image: "✊" },
    { letter: "F", instruction: "Touch thumb and index finger, other fingers up", image: "👌" }
  ];

  const fullText = (() => {
    if (mode === "intro") return "Beginner track";
    if (mode === "learning") return `Learn the letter "${letters[currentIndex].letter}"`;
    return "Time to test your knowledge!";
  })();

  useEffect(() => {
    setDisplayedText("");
    setIsTyping(true);
    let index = 0;

    const timer = setInterval(() => {
      if (index < fullText.length) {
        setDisplayedText(fullText.slice(0, index + 1));
        index++;
      } else {
        setIsTyping(false);
        clearInterval(timer);
      }
    }, 45);

    return () => clearInterval(timer);
  }, [currentIndex, mode, fullText]);

  const handleContinue = () => {
    if (currentIndex < letters.length - 1) {
      setCurrentIndex(currentIndex + 1);
    } else {
      setMode("quiz");
      setCurrentIndex(0);
      setShownHints({});
    }
  };

  const handleQuizAnswer = (index: number, answer: string) => {
    setQuizAnswers({ ...quizAnswers, [index]: (answer || "").toUpperCase() });
  };

  const handleSubmitQuiz = () => setMode("results");

  const handleStartTrack = () => {
    setMode("learning");
    setCurrentIndex(0);
  };

  const handleRestart = () => {
    setCurrentIndex(0);
    setMode("learning");
    setQuizAnswers({});
    setShownHints({});
  };

  const calculateScore = () => {
    let correct = 0;
    letters.forEach((letter, idx) => {
      if (quizAnswers[idx] === letter.letter) correct++;
    });
    return correct;
  };

  // shared layout wrapper
  const Wrapper = ({ children }: { children: React.ReactNode }) => (
    <div className="beginner-page">
      <div className="beginner-card">{children}</div>
    </div>
  );

  const Title = () => (
    <div className="beginner-titleRow">
      <h1 className="beginner-title">
        {displayedText}
        {isTyping && <span className="beginner-caret">|</span>}
      </h1>
    </div>
  );

  if (mode === "intro") {

    return (
      <Wrapper>
        <Title />

        <div className="beginner-introPanel">
          <div className="beginner-emoji">👋</div>
          <h2 className="beginner-introTitle">Start learning the ASL alphabet</h2>
          <p className="beginner-introSubtitle">
            Work through {letters.length} signs, then take a short quiz. Use hints whenever you get
            stuck.
          </p>
          <ul className="beginner-introList">
            <li>Step-by-step sign instructions</li>
            <li>Quick quiz to check recall</li>
            <li>Hints available during the quiz</li>
          </ul>
        </div>

        <button className="beginner-btn primary" onClick={handleStartTrack}>
          <span>Start Beginner Track</span>
          <ChevronRight size={20} />
        </button>
      </Wrapper>
    );
  }

  if (mode === "learning") {
    const progress = ((currentIndex + 1) / letters.length) * 100;

    return (
      <Wrapper>
        <Title />

        <div className="beginner-panel">
          <div className="beginner-emoji">{letters[currentIndex].image}</div>
          <div className="beginner-letter">{letters[currentIndex].letter}</div>
          <p className="beginner-instruction">{letters[currentIndex].instruction}</p>
        </div>

        <div className="beginner-progressBlock">
          <div className="beginner-progressMeta">
            <span>Progress</span>
            <span>
              {currentIndex + 1} / {letters.length}
            </span>
          </div>

          <div className="beginner-progressTrack">
            <div className="beginner-progressFill" style={{ width: `${progress}%` }} />
          </div>
        </div>

        <button className="beginner-btn primary" onClick={handleContinue}>
          <span>{currentIndex < letters.length - 1 ? "Continue" : "Start Quiz"}</span>
          <ChevronRight size={20} />
        </button>
      </Wrapper>
    );
  }

  if (mode === "results") {
    const score = calculateScore();
    const perfect = score === letters.length;
    const ok = score >= letters.length / 2;

    return (
      <Wrapper>
        <h1 className="beginner-resultsTitle">Quiz Results</h1>

        <div className="beginner-scorePanel">
          <div className="beginner-score">
            {score} <span className="beginner-scoreSlash">/ {letters.length}</span>
          </div>
          <p className="beginner-scoreText">
            {perfect ? "Perfect! 🎉" : ok ? "Good job! 👏" : "Keep practicing! 💪"}
          </p>
        </div>

        <div className="beginner-resultsList">
          {letters.map((letter, idx) => {
            const correct = quizAnswers[idx] === letter.letter;
            return (
              <div className="beginner-resultRow" key={idx}>
                <span className="beginner-resultEmoji">{letter.image}</span>
                <span className="beginner-resultLetter">{letter.letter}</span>
                <span className={`beginner-resultMark ${correct ? "good" : "bad"}`}>
                  {correct ? "✓" : `✗ (${quizAnswers[idx] || "-"})`}
                </span>
              </div>
            );
          })}
        </div>

        <button className="beginner-btn primary" onClick={handleRestart}>
          <RotateCcw size={18} />
          <span>Restart Learning</span>
        </button>
      </Wrapper>
    );
  }

  const isComplete = Object.keys(quizAnswers).length >= letters.length;

  return (
    <Wrapper>
      <Title />
      <p className="beginner-subtitle">Type the letter for each sign:</p>

      <div className="beginner-quizList">
        {letters.map((letter, idx) => (
          <div className="beginner-quizRow" key={idx}>
            <span className="beginner-quizEmoji">{letter.image}</span>
            <div className="beginner-quizContent">
              <div className="beginner-quizControls">
                <input
                  type="text"
                  maxLength={1}
                  value={quizAnswers[idx] || ""}
                  onChange={(e) => handleQuizAnswer(idx, e.target.value)}
                  className="beginner-input"
                  placeholder="?"
                  inputMode="text"
                  aria-label={`Answer for sign ${idx + 1}`}
                />
                <button
                  type="button"
                  className="beginner-hintButton"
                  onClick={() =>
                    setShownHints((prev) => ({ ...prev, [idx]: !prev[idx] }))
                  }
                >
                  {shownHints[idx] ? "Hide hint" : "Show hint"}
                </button>
              </div>
              {shownHints[idx] && (
                <p className="beginner-hintText">{letter.instruction}</p>
              )}
            </div>
          </div>
        ))}
      </div>

      <button
        className={`beginner-btn primary ${!isComplete ? "disabled" : ""}`}
        onClick={handleSubmitQuiz}
        disabled={!isComplete}
      >
        Submit Quiz
      </button>
    </Wrapper>
  );
};

export default Beginner;
