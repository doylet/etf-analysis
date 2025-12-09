/**
 * Widget Services Provider - React Context for SOLID Widget Architecture
 * Provides dependency injection container for widget services
 */

import React, { createContext, ReactNode } from 'react';
import { IWidgetFactory } from '../interfaces/IWidgetFactory';
import { WidgetFactory } from '../factories/WidgetFactory';

export interface IEventBus {
  subscribe<T = unknown>(event: string, callback: (data: T) => void): () => void;
  publish<T = unknown>(event: string, data: T): void;
  getSubscriptions(): Record<string, number>;
}

export interface ILogger {
  debug(message: string, meta?: Record<string, unknown>): void;
  info(message: string, meta?: Record<string, unknown>): void;
  warn(message: string, meta?: Record<string, unknown>): void;
  error(message: string, error?: Error, meta?: Record<string, unknown>): void;
}

// Simple Event Bus Implementation
class EventBus implements IEventBus {
  private listeners = new Map<string, Set<(data: any) => void>>();

  subscribe<T = unknown>(event: string, callback: (data: T) => void): () => void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    
    this.listeners.get(event)!.add(callback);
    
    return () => {
      this.listeners.get(event)?.delete(callback);
    };
  }

  publish<T = unknown>(event: string, data: T): void {
    this.listeners.get(event)?.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`Error in event listener for ${event}:`, error);
      }
    });
  }

  getSubscriptions(): Record<string, number> {
    const subscriptions: Record<string, number> = {};
    for (const [event, listeners] of this.listeners.entries()) {
      subscriptions[event] = listeners.size;
    }
    return subscriptions;
  }
}

// Simple Console Logger Implementation
class ConsoleLogger implements ILogger {
  debug(message: string, meta?: Record<string, unknown>): void {
    console.debug(`[DEBUG] ${message}`, meta);
  }

  info(message: string, meta?: Record<string, unknown>): void {
    console.info(`[INFO] ${message}`, meta);
  }

  warn(message: string, meta?: Record<string, unknown>): void {
    console.warn(`[WARN] ${message}`, meta);
  }

  error(message: string, error?: Error, meta?: Record<string, unknown>): void {
    console.error(`[ERROR] ${message}`, error, meta);
  }
}

// Widget services container
export interface WidgetServices {
  factory: IWidgetFactory;
  eventBus: IEventBus;
  logger: ILogger;
}

// Create the context
export const WidgetServicesContext = createContext<WidgetServices | null>(null);

// Default services implementation
const createDefaultServices = (): WidgetServices => ({
  factory: WidgetFactory.createWithDefaults(),
  eventBus: new EventBus(),
  logger: new ConsoleLogger()
});

// Provider component
interface WidgetServicesProviderProps {
  children: ReactNode;
  services?: WidgetServices;
}

export function WidgetServicesProvider({ 
  children, 
  services = createDefaultServices() 
}: WidgetServicesProviderProps) {
  return (
    <WidgetServicesContext.Provider value={services}>
      {children}
    </WidgetServicesContext.Provider>
  );
}

// Export types for external use
// WidgetServices interface is already exported above