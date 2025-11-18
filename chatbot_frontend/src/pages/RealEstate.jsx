import ChatTemplate from "../components/ChatTemplate";

export default function RealEstate() {
  return (
    <ChatTemplate
      apiEndpoint="http://127.0.0.1:5002/api/real-estate/chat"
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
