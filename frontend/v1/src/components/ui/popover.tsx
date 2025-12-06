'use client';

import React, { useState, useMemo } from 'react';
import { Popover as BasePopover } from '@base-ui-components/react/popover';
import { cn } from '@/lib/utils';
import { applyVariant } from '@/lib/base-ui-utils';
import type { ComponentStyleConfig, BaseUIComponentProps } from '@/lib/base-ui-types';

// Notification interface
export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  type: 'info' | 'warning' | 'error' | 'success';
  actionUrl?: string;
}

// NotificationPopover Props
export interface NotificationPopoverProps extends Omit<BaseUIComponentProps, 'variant'> {
  notifications?: NotificationItem[];
  onMarkAsRead?: (notificationId: string) => void;
  onMarkAllAsRead?: () => void;
  onNotificationClick?: (notification: NotificationItem) => void;
  unreadCount?: number;
  maxDisplayed?: number;
  size?: 'sm' | 'md' | 'lg';
  variant?: 'default' | 'elevated';
}

// Style configuration for NotificationPopover
const popoverStyles: ComponentStyleConfig = {
  base: "z-50 rounded-lg border border-gray-200 bg-white shadow-lg dark:border-gray-800 dark:bg-gray-900 max-w-sm min-w-0 w-full",
  variants: {
    default: "border-gray-200 bg-white dark:border-gray-800 dark:bg-gray-900",
    elevated: "shadow-xl border-gray-100 bg-white dark:border-gray-700 dark:bg-gray-800"
  },
  sizes: {
    sm: "w-64 max-w-xs",
    md: "w-80 max-w-sm", 
    lg: "w-96 max-w-md"
  }
};

const triggerStyles: ComponentStyleConfig = {
  base: "relative inline-flex items-center justify-center rounded-md p-2 text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  variants: {
    default: "bg-gray-100 text-gray-900 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-100 dark:hover:bg-gray-700",
    ghost: "text-gray-600 hover:bg-gray-100 hover:text-gray-900 dark:text-gray-400 dark:hover:bg-gray-800 dark:hover:text-gray-100"
  },
  sizes: {
    sm: "h-8 w-8",
    md: "h-10 w-10", 
    lg: "h-12 w-12"
  }
};

// ArrowIcon component
export const ArrowIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg
    className={cn("h-4 w-4", className)}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="m18 15-6-6-6 6" />
  </svg>
);

// BellIcon component
export const BellIcon: React.FC<{ className?: string }> = ({ className }) => (
  <svg
    className={cn("h-5 w-5", className)}
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M6 8a6 6 0 0 1 12 0c0 7 3 9 3 9H3s3-2 3-9" />
    <path d="M10.3 21a1.94 1.94 0 0 0 3.4 0" />
  </svg>
);

// NotificationBadge component
const NotificationBadge: React.FC<{ count: number; className?: string }> = ({ count, className }) => {
  if (count === 0) return null;
  
  return (
    <span className={cn(
      "absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-xs font-medium text-white flex items-center justify-center",
      className
    )}>
      {count > 99 ? '99+' : count}
    </span>
  );
};

// Create the formatter outside the component to avoid recreating on each render
const relativeTimeFormatter = new Intl.RelativeTimeFormat('en', { numeric: 'auto' });

// NotificationItem component
const NotificationItemComponent: React.FC<{
  notification: NotificationItem;
  onMarkAsRead?: (id: string) => void;
  onNotificationClick?: (notification: NotificationItem) => void;
}> = ({ notification, onMarkAsRead, onNotificationClick }) => {
  const typeColors = {
    info: 'text-blue-600 dark:text-blue-400',
    warning: 'text-yellow-600 dark:text-yellow-400', 
    error: 'text-red-600 dark:text-red-400',
    success: 'text-green-600 dark:text-green-400'
  };

  const relativeTime = useMemo(() => {
    const hoursDiff = Math.ceil((notification.timestamp.getTime() - new Date().getTime()) / (1000 * 60 * 60));
    return relativeTimeFormatter.format(hoursDiff, 'hour');
  }, [notification.timestamp]);

  const handleClick = () => {
    if (!notification.read && onMarkAsRead) {
      onMarkAsRead(notification.id);
    }
    if (onNotificationClick) {
      onNotificationClick(notification);
    }
  };

  return (
    <div
      className={cn(
        "border-b border-gray-100 p-2 sm:p-3 hover:bg-gray-50 cursor-pointer transition-colors dark:border-gray-800 dark:hover:bg-gray-800/50",
        !notification.read && "bg-blue-50/50 dark:bg-blue-900/10"
      )}
      onClick={handleClick}
    >
      <div className="flex items-start space-x-2 sm:space-x-3">
        <div className={cn("mt-1 h-2 w-2 rounded-full flex-shrink-0", 
          notification.read ? "bg-gray-300" : typeColors[notification.type]
        )} />
        <div className="flex-1 min-w-0">
          <p className={cn(
            "text-xs sm:text-sm font-medium truncate",
            notification.read ? "text-gray-600 dark:text-gray-400" : "text-gray-900 dark:text-gray-100"
          )}>
            {notification.title}
          </p>
          <p className="text-xs sm:text-sm text-gray-500 dark:text-gray-500 mt-1 line-clamp-2">
            {notification.message}
          </p>
          <p className="text-xs text-gray-400 dark:text-gray-600 mt-1 sm:mt-2">
            {relativeTime}
          </p>
        </div>
      </div>
    </div>
  );
};

// Main NotificationPopover component
export const NotificationPopover: React.FC<NotificationPopoverProps> = ({
  notifications = [],
  onMarkAsRead,
  onMarkAllAsRead,
  onNotificationClick,
  unreadCount = 0,
  maxDisplayed = 5,
  variant = 'default',
  size = 'md',
  className,
  ...props
}) => {
  const [open, setOpen] = useState(false);
  
  const displayedNotifications = notifications.slice(0, maxDisplayed);
  const hasMore = notifications.length > maxDisplayed;

  const popoverClasses = applyVariant(popoverStyles, variant, size);
  const triggerClasses = applyVariant(triggerStyles, 'ghost', size);

  return (
    <BasePopover.Root open={open} onOpenChange={setOpen}>
      <BasePopover.Trigger
        className={cn(triggerClasses, className)}
        aria-label={`Notifications ${unreadCount > 0 ? `(${unreadCount} unread)` : ''}`}
        {...props}
      >
        <BellIcon />
        <NotificationBadge count={unreadCount} />
      </BasePopover.Trigger>

      <BasePopover.Portal>
        <BasePopover.Positioner 
          side="bottom" 
          align="end" 
          sideOffset={8}
        >
          <BasePopover.Popup className={cn(
            popoverClasses, 
            "animate-in fade-in-0 zoom-in-95",
            "max-h-[80vh] sm:max-h-96", // Responsive height limits
            "mx-4 sm:mx-0" // Margin on mobile
          )}>
            <BasePopover.Arrow>
              <ArrowIcon className="fill-white dark:fill-gray-900 text-gray-200 dark:text-gray-800" />
            </BasePopover.Arrow>
            
            <div className="flex items-center justify-between p-3 sm:p-4 border-b border-gray-200 dark:border-gray-800">
              <h3 className="font-semibold text-gray-900 dark:text-gray-100 text-sm sm:text-base">
                Notifications
              </h3>
              {unreadCount > 0 && onMarkAllAsRead && (
                <button 
                  onClick={() => {
                    onMarkAllAsRead();
                    setOpen(false);
                  }}
                  className="text-xs sm:text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 font-medium shrink-0"
                >
                  Mark all read
                </button>
              )}
            </div>

            <div className="max-h-64 sm:max-h-80 overflow-y-auto">
              {displayedNotifications.length === 0 ? (
                <div className="p-6 sm:p-8 text-center">
                  <BellIcon className="mx-auto h-10 w-10 sm:h-12 sm:w-12 text-gray-400 dark:text-gray-600" />
                  <p className="mt-2 text-xs sm:text-sm text-gray-500 dark:text-gray-400">
                    No notifications yet
                  </p>
                </div>
              ) : (
                <>
                  {displayedNotifications.map((notification) => (
                    <NotificationItemComponent
                      key={notification.id}
                      notification={notification}
                      onMarkAsRead={onMarkAsRead}
                      onNotificationClick={onNotificationClick}
                    />
                  ))}
                  {hasMore && (
                    <div className="p-3 text-center border-t border-gray-200 dark:border-gray-800">
                      <button className="text-sm text-blue-600 hover:text-blue-800 dark:text-blue-400 dark:hover:text-blue-200 font-medium">
                        View all notifications
                      </button>
                    </div>
                  )}
                </>
              )}
            </div>
          </BasePopover.Popup>
        </BasePopover.Positioner>
      </BasePopover.Portal>
    </BasePopover.Root>
  );
};

export default NotificationPopover;