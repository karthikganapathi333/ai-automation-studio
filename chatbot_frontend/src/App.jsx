import { Routes, Route } from "react-router-dom";

import Home from "./pages/Home";
import RealEstate from "./pages/RealEstate";
import StudentMentor from "./pages/StudentMentor";
import FitnessCoach from "./pages/FitnessCoach";
import Restaurant from "./pages/Restaurant";
import TravelPlanner from "./pages/TravelPlanner";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/chat/real-estate" element={<RealEstate />} />
      <Route path="/chat/student-mentor" element={<StudentMentor />} />
      <Route path="/chat/fitness-coach" element={<FitnessCoach />} />
      <Route path="/chat/restaurant" element={<Restaurant />} />
      <Route path="/chat/travel-planner" element={<TravelPlanner />} />
    </Routes>
  );
}
