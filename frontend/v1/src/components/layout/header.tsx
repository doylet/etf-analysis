"use client";

import React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Notifications } from "@/components/features/notifications";
import { Button } from "@/components/ui/button";
import { StatusIndicator } from "@/components/ui/status-indicator";
import { ModeToggle } from "@/components/ui/mode-toggle";
import { User, ChevronRight, Home, BarChart3 } from "lucide-react";

interface HeaderProps {
  userName?: string;
  title?: string;
  subtitle?: string;
  status?: "live" | "delayed" | "stale" | "error";
}

// Breadcrumb helper function
const generateBreadcrumbs = (pathname: string) => {
  const segments = pathname.split("/").filter(Boolean);
  const breadcrumbs = [{ label: "Home", href: "/" }];

  let currentPath = "";
  segments.forEach((segment) => {
    currentPath += `/${segment}`;
    const label = segment.charAt(0).toUpperCase() + segment.slice(1);
    breadcrumbs.push({ label, href: currentPath });
  });

  return breadcrumbs;
};

export const Header: React.FC<HeaderProps> = ({
  userName = "User",
  title = "ETF Analysis",
  status = "live",
}) => {
  const pathname = usePathname();
  const breadcrumbs = generateBreadcrumbs(pathname);

  const handleLogout = () => {
    // Handle logout logic
    console.log("Logout clicked");
    // TODO: Implement actual logout logic here
  };

  return (
    <header className="bg-background border-b border-border shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center py-4">
          {/* Left side - Brand and Navigation */}
          <div className="flex items-center space-x-6">
            {/* Brand */}
            <div className="flex items-center space-x-3">
              <div className="flex items-center justify-center w-8 h-8 bg-scheme-primary rounded-lg">
                <BarChart3 className="h-5 w-5 text-white" />
              </div>
              <div className="flex flex-col">
                <h1 className="text-lg font-semibold text-foreground tabular-nums">
                  {title}
                </h1>
                {/* Breadcrumbs */}
                <nav className="hidden md:flex items-center space-x-1 text-sm">
                  {breadcrumbs.map((breadcrumb, index) => (
                    <React.Fragment key={breadcrumb.href}>
                      {index > 0 && (
                        <ChevronRight className="h-3 w-3 text-muted-foreground" />
                      )}
                      <Link
                        href={breadcrumb.href}
                        className={`${
                          index === breadcrumbs.length - 1
                            ? "text-foreground font-medium"
                            : "text-muted-foreground hover:text-foreground"
                        } transition-colors px-2 py-1 rounded-md hover:bg-muted`}
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
            </div>
          </div>
          <StatusIndicator
            variant={
              status === "live"
                ? "success"
                : status === "delayed"
                ? "warning"
                : "danger"
            }
            size="sm"
          >
            {status === "live"
              ? "Live Data"
              : status === "delayed"
              ? "Delayed"
              : "Data Issues"}
          </StatusIndicator>

          {/* Right side - User info and actions */}
          <div className="flex items-center space-x-4">
            {/* Theme Controls */}
            <div className="hidden lg:flex items-center space-x-3">
              <ModeToggle />
            </div>

            {/* User info */}
            <div className="hidden sm:flex items-center space-x-3 px-3 py-1.5 bg-muted/50 rounded-lg">
              <div className="flex items-center justify-center w-6 h-6 bg-muted rounded-full">
                <User className="h-3 w-3 text-muted-foreground" />
              </div>
              <span className="text-sm font-medium text-foreground">
                {userName}
              </span>
            </div>

            <Notifications />

            <Button onClick={handleLogout} variant="ghost" size="sm">
              <span className="hidden sm:inline">Sign Out</span>
            </Button>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
