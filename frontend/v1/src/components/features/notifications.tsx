'use client';

import React from 'react';
import { NotificationPopover } from '@/components/ui/popover';
import { useNotifications } from '@/hooks/use-notifications';

interface NotificationsProps {
  className?: string;
}

/**
 * Notifications - A smart component that handles notification state
 * and provides the notification popover with data and handlers.
 * 
 * This component connects the notification UI (NotificationPopover) 
 * with the notification state management (useNotifications hook).
 */
export const Notifications: React.FC<NotificationsProps> = ({ 
  className = '' 
}) => {
  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    handleNotificationClick
  } = useNotifications();

  return (
    <NotificationPopover
      notifications={notifications}
      unreadCount={unreadCount}
      onMarkAsRead={markAsRead}
      onMarkAllAsRead={markAllAsRead}
      onNotificationClick={handleNotificationClick}
      maxDisplayed={4}
      variant="default"
      size="md"
      className={className}
    />
  );
};

export default Notifications;