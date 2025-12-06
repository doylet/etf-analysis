'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Notifications } from '@/components/features/notifications';
import { Button } from '@/components/ui/button';
import { LogOut, User, ChevronRight, Home } from 'lucide-react';

interface HeaderProps {
  userName?: string;
  title?: string;
  subtitle?: string;
}

// Breadcrumb helper function
const generateBreadcrumbs = (pathname: string) => {
  const segments = pathname.split('/').filter(Boolean);
  const breadcrumbs = [{ label: 'Home', href: '/' }];
  
  let currentPath = '';
  segments.forEach((segment) => {
    currentPath += `/${segment}`;
    const label = segment.charAt(0).toUpperCase() + segment.slice(1);
    breadcrumbs.push({ label, href: currentPath });
  });
  
  return breadcrumbs;
};

export const Header: React.FC<HeaderProps> = ({
  userName = 'User',
  title = 'ETF Analysis'
}) => {
  const pathname = usePathname();
  const breadcrumbs = generateBreadcrumbs(pathname);
  
  const handleLogout = () => {
    // Handle logout logic
    console.log('Logout clicked');
    // TODO: Implement actual logout logic here
  };

  return (
    <header className="bg-white border-b">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-3">
          {/* Left side - Title and Breadcrumbs */}
          <div className="flex flex-col space-y-1">
            <h1 className="text-xl font-bold text-gray-900">{title}</h1>
            
            {/* Breadcrumbs */}
            <nav className="flex items-center space-x-1 text-sm">
              {breadcrumbs.map((breadcrumb, index) => (
                <React.Fragment key={breadcrumb.href}>
                  {index > 0 && (
                    <ChevronRight className="h-3 w-3 text-gray-400" />
                  )}
                  <Link
                    href={breadcrumb.href}
                    className={`${
                      index === breadcrumbs.length - 1
                        ? 'text-gray-900 font-medium'
                        : 'text-gray-500 hover:text-gray-700'
                    } transition-colors`}
                  >
                    {index === 0 ? (
                      <Home className="h-3 w-3" />
                    ) : (
                      breadcrumb.label
                    )}
                  </Link>
                </React.Fragment>
              ))}
            </nav>
          </div>
          
          {/* Right side - User info and actions */}
          <div className="flex items-center space-x-3">
            <div className="flex items-center space-x-2 text-sm text-gray-600">
              <User className="h-4 w-4" />
              <span>{userName}</span>
            </div>
            
            <Notifications />
            
            <Button
              onClick={handleLogout}
              variant="outline"
              size="sm"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;