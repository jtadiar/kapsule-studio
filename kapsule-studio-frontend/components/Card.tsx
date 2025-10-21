import React from 'react';

interface CardProps {
  title: string | React.ReactNode;
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ title, children, className = '' }) => {
  return (
    <div className={`bg-white border border-gray-200 rounded-2xl shadow-md overflow-hidden ${className}`}>
      <div className="p-6">
        <h2 className="text-xl font-semibold text-gray-800 mb-4">{title}</h2>
        {children}
      </div>
    </div>
  );
};