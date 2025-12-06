'use client';

import { useState, useCallback } from 'react';
import { type NotificationItem } from '@/components/ui/popover';

// Sample notification data - in real app this would come from an API or context
const initialNotifications: NotificationItem[] = [
  {
    id: '1',
    title: 'Portfolio Rebalancing',
    message: 'Your portfolio allocation has drifted by 5%. Consider rebalancing.',
    timestamp: new Date(Date.now() - 1000 * 60 * 30), // 30 minutes ago
    read: false,
    type: 'warning'
  },
  {
    id: '2', 
    title: 'Market Update',
    message: 'S&P 500 closed up 2.1% today. Your portfolio gained $1,245.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
    read: false,
    type: 'success'
  },
  {
    id: '3',
    title: 'Dividend Payment',
    message: 'Received $87.50 in dividend payments from VANGUARD ETFs.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24), // 1 day ago
    read: true,
    type: 'info'
  },
  {
    id: '4',
    title: 'Analysis Complete',
    message: 'Your monthly portfolio analysis report is ready to view.',
    timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 2), // 2 days ago
    read: true,
    type: 'info'
  }
];

export const useNotifications = () => {
  const [notifications, setNotifications] = useState<NotificationItem[]>(initialNotifications);
  
  const unreadCount = notifications.filter(n => !n.read).length;

  const markAsRead = useCallback((notificationId: string) => {
    setNotifications(prev => 
      prev.map(notification => 
        notification.id === notificationId 
          ? { ...notification, read: true }
          : notification
      )
    );
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications(prev =>
      prev.map(notification => ({ ...notification, read: true }))
    );
  }, []);

  const handleNotificationClick = useCallback((notification: NotificationItem) => {
    // Handle navigation or action based on notification type
    console.log('Notification clicked:', notification);
    
    // Mark as read if not already read
    if (!notification.read) {
      markAsRead(notification.id);
    }
  }, [markAsRead]);

  return {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
    handleNotificationClick
  };
};