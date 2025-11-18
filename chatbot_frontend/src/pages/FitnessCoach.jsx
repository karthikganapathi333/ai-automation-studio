import ChatTemplate from "../components/ChatTemplate";

export default function FitnessCoach() {
  return (
    <ChatTemplate
      apiEndpoint="http://127.0.0.1:5002/api/fitness-coach/chat"
      headerTitle="Fitness Coach"
      routeName="Fitness Coach"
      suggestions={[
        "Create a 4-week gym plan",
        "How many calories to lose 1kg?",
        "Best exercises for abs",
        "Give me a weight loss diet"
      ]}
    />
  );
}
