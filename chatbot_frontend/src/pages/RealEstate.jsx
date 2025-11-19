import ChatTemplate from "../components/ChatTemplate";

export default function RealEstate() {
  return (
    <ChatTemplate
      apiEndpoint="/chatbot_api_proxy/api/real-estate/chat"
      headerTitle="Real Estate Assistant"
      routeName="Real Estate"
      suggestions={[
        "Show me homes in my budget",
        "What should I know before buying?",
        "Explain property investment",
        "Check property documents"
      ]}
    />
  );
}
