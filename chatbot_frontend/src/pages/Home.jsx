import { Link } from "react-router-dom";

export default function Home() {
  const bots = [
    {
      name: "Real Estate Assistant",
      route: "/chat/real-estate",
      desc: "Buy, sell, invest — expert guidance.",
      icon: "🏡",
    },
    {
      name: "Student Mentor",
      route: "/chat/student-mentor",
      desc: "Study tips, career & exam support.",
      icon: "🎓",
    },
    {
      name: "Fitness Coach",
      route: "/chat/fitness-coach",
      desc: "Workout routines & diet plans.",
      icon: "💪",
    },
    {
      name: "Restaurant Assistant",
      route: "/chat/restaurant",
      desc: "Menu ideas, kitchen operations, planning.",
      icon: "🍽️",
    },
    {
      name: "Travel Planner",
      route: "/chat/travel-planner",
      desc: "Trips, itinerary & budget travel.",
      icon: "✈️",
    },
  ];

  return (
    <div className="home-container">

      {/* HERO TITLE */}
      <h1 className="home-title">AI Chatbots</h1>
      <p className="home-sub">Explore our interactive AI assistants.</p>

      {/* CARD GRID */}
      <div className="bot-grid">
        {bots.map((b, i) => (
          <Link to={b.route} className="bot-card" key={i}>
            <div className="bot-icon">{b.icon}</div>
            <h3 className="bot-name">{b.name}</h3>
            <p className="bot-desc">{b.desc}</p>
          </Link>
        ))}
      </div>
    </div>
  );
}
