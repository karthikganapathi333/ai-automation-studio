import ChatTemplate from "../components/ChatTemplate";

export default function TravelPlanner() {
  return (
    <ChatTemplate
      apiEndpoint="/chatbot_api_proxy/api/travel-planner/chat"
      headerTitle="Travel Planner"
      routeName="Travel Planner"
      suggestions={[
        "Plan a 5-day trip to Goa",
        "Budget travel tips for Europe",
        "Best time to visit Hampi",
        "Low-cost travel ideas"
      ]}
    />
  );
}
