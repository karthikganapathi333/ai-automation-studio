import ChatTemplate from "../components/ChatTemplate";

export default function Restaurant() {
  return (
    <ChatTemplate
      apiEndpoint="/chatbot_api_proxy/api/restaurant/chat"
      headerTitle="Restaurant Assistant"
      routeName="Restaurant"
      suggestions={[
        "Suggest a 3-course menu",
        "Create a spicy vegetarian dish",
        "How to improve delivery time?",
        "Best items to add to menu"
      ]}
    />
  );
}
