const sendMessage = async () => {
  if (!input.trim()) return;

  const userMessage: Message = {
    id: Date.now().toString(),
    role: 'user',
    content: input,
    timestamp: new Date(),
  };

  setMessages(prev => [...prev, userMessage]);
  setInput('');
  setLoading(true);
  setShowQuickActions(false);

  try {
    // IMPORTANT: Make sure this URL matches your backend
    const response = await axios.post('http://localhost:8000/api/v1/ai/chat?user_id=1', {
      message: input,
      stream: false,
      thinking: showThinking
    });

    // Check if response has the expected structure
    let assistantContent = '';
    if (response.data.choices && response.data.choices[0] && response.data.choices[0].message) {
      assistantContent = response.data.choices[0].message.content;
    } else if (response.data.content) {
      assistantContent = response.data.content;
    } else {
      assistantContent = JSON.stringify(response.data);
    }

    const assistantMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: assistantContent,
      timestamp: new Date(),
      thinking: response.data.choices?.[0]?.message?.reasoning_content
    };

    setMessages(prev => [...prev, assistantMessage]);
  } catch (error) {
    console.error('Error sending message:', error);
    
    const errorMessage: Message = {
      id: (Date.now() + 1).toString(),
      role: 'assistant',
      content: 'Sorry, I encountered an error connecting to the AI service. Please make sure the backend is running on port 8000.',
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, errorMessage]);
  } finally {
    setLoading(false);
  }
};
