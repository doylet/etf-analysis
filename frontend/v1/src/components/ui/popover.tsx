import * as React from "react"
import * as PopoverPrimitive from "@radix-ui/react-popover"

import { cn } from "@/lib/utils"

const Popover = PopoverPrimitive.Root

const PopoverTrigger = PopoverPrimitive.Trigger

const PopoverContent = React.forwardRef<
  React.ElementRef<typeof PopoverPrimitive.Content>,
  React.ComponentPropsWithoutRef<typeof PopoverPrimitive.Content>
>(({ className, align = "center", sideOffset = 4, ...props }, ref) => (
  <PopoverPrimitive.Portal>
    <PopoverPrimitive.Content
      ref={ref}
      align={align}
      sideOffset={sideOffset}
      className={cn(
        "z-50 w-72 rounded-md border bg-popover p-4 text-popover-foreground shadow-md outline-none data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0 data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95 data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2 data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2",
        className
      )}
      {...props}
    />
  </PopoverPrimitive.Portal>
))
PopoverContent.displayName = PopoverPrimitive.Content.displayName

// Temporary compatibility layer for NotificationPopover
export interface NotificationItem {
  id: string;
  title: string;
  message: string;
  timestamp: Date;
  read: boolean;
  type?: 'info' | 'success' | 'warning' | 'error';
}

interface NotificationPopoverProps {
  notifications: NotificationItem[];
  unreadCount: number;
  onMarkAsRead: (id: string) => void;
  onMarkAllAsRead: () => void;
  onNotificationClick: (notification: NotificationItem) => void;
  maxDisplayed?: number;
  variant?: string;
  size?: string;
  className?: string;
}

export const NotificationPopover: React.FC<NotificationPopoverProps> = ({
  notifications,
  unreadCount,
  className,
}) => {
  return (
    <Popover>
      <PopoverTrigger asChild>
        <button className={cn("relative", className)}>
          <span className="sr-only">Notifications</span>
          {unreadCount > 0 && (
            <span className="absolute -top-1 -right-1 h-4 w-4 rounded-full bg-destructive text-xs text-destructive-foreground flex items-center justify-center">
              {unreadCount}
            </span>
          )}
          🔔
        </button>
      </PopoverTrigger>
      <PopoverContent>
        <div className="space-y-2">
          <h4 className="font-medium leading-none">Notifications</h4>
          {notifications.length === 0 ? (
            <p className="text-sm text-muted-foreground">No notifications</p>
          ) : (
            <div className="space-y-2">
              {notifications.slice(0, 4).map((notification) => (
                <div key={notification.id} className="text-sm">
                  <p className="font-medium">{notification.title}</p>
                  <p className="text-muted-foreground">{notification.message}</p>
                </div>
              ))}
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  )
}

export { Popover, PopoverTrigger, PopoverContent }
