'use client';

interface QuickActionsProps {
  onSelect: (question: string) => void;
}

export default function QuickActions({ onSelect }: QuickActionsProps) {
  const actions = [
    { icon: '📊', text: 'How to improve win rate?', color: 'bg-blue-600' },
    { icon: '📉', text: 'Risk management tips', color: 'bg-purple-600' },
    { icon: '🧠', text: 'Trading psychology', color: 'bg-green-600' },
    { icon: '📈', text: 'Analyze my last trade', color: 'bg-orange-600' },
    { icon: '🎯', text: 'Set trading goals', color: 'bg-pink-600' },
    { icon: '📅', text: 'Weekly review', color: 'bg-indigo-600' },
  ];

  return (
    <div className="grid grid-cols-2 gap-2 p-2">
      {actions.map((action, index) => (
        <button
          key={index}
          onClick={() => onSelect(action.text)}
          className={`${action.color} text-white p-2 rounded-lg text-xs hover:opacity-90 transition flex items-center gap-1`}
        >
          <span>{action.icon}</span>
          <span className="truncate">{action.text}</span>
        </button>
      ))}
    </div>
  );
}
