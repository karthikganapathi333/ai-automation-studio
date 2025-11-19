import ChatTemplate from "../components/ChatTemplate";

export default function StudentMentor() {
  return (
    <ChatTemplate
      apiEndpoint="/chatbot_api_proxy/api/student-mentor/chat"
      headerTitle="Student Mentor"
      routeName="Student Mentor"
      suggestions={[
        "How do I prepare for exams?",
        "Which career should I choose?",
        "Give me study tips.",
        "Help me manage time"
      ]}
    />
  );
}
