'use client';

import React from 'react';
import { Notifications } from '@/components/features/notifications';
import { Button } from '@/components/shared';
import { LogOut, User, BarChart3 } from 'lucide-react';

interface HeaderProps {
  userName?: string;
  title?: string;
  subtitle?: string;
}

export const Header: React.FC<HeaderProps> = ({
  userName = 'User',
  title = 'ETF Analysis',
  subtitle = 'NextJS Dashboard'
}) => {
  const handleLogout = () => {
    // Handle logout logic
    console.log('Logout clicked');
    // TODO: Implement actual logout logic here
  };

  return (
    <header className="bg-white shadow">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-blue-500 rounded-lg">
              <BarChart3 className="h-6 w-6 text-white" />
            </div>
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{title}</h1>
              <p className="text-sm text-gray-600">{subtitle}</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-2">
              <User className="h-4 w-4 text-gray-500" />
              <span className="text-sm text-gray-700">
                Welcome, {userName}
              </span>
            </div>
            
            {/* Notifications */}
            <Notifications />
            
            <Button
              onClick={handleLogout}
              variant="outline"
              size="sm"
              className="flex items-center space-x-2"
            >
              <LogOut className="h-4 w-4" />
              <span className="text-sm">Logout</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;