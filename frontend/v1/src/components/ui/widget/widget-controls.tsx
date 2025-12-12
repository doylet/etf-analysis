/**
 * Widget Controls
 * Reusable form control components for dashboard widgets
 */

import React from 'react';
import { cn } from '@/lib/utils';

interface WidgetSelectProps<T extends string = string> {
  value: T;
  onChange: (value: T) => void;
  options: readonly { value: T; label: string }[];
  disabled?: boolean;
  className?: string;
  label?: string;
}

export function WidgetSelect<T extends string = string>({
  value,
  onChange,
  options,
  disabled = false,
  className = '',
  label,
}: WidgetSelectProps<T>) {
  return (
    <div className="flex flex-col gap-1">
      {label && (
        <label className="text-xs text-muted-foreground">{label}</label>
      )}
      <select
        value={value}
        onChange={(e) => onChange(e.target.value as T)}
        disabled={disabled}
        className={cn(
          'px-2 py-1 text-sm border border-border rounded-md bg-background',
          className
        )}
      >
        {options.map((opt) => (
          <option key={opt.value} value={opt.value}>
            {opt.label}
          </option>
        ))}
      </select>
    </div>
  );
}

interface WidgetSliderProps {
  value: number;
  onChange: (value: number) => void;
  min: number;
  max: number;
  step?: number;
  label: string;
  showValue?: boolean;
  disabled?: boolean;
  className?: string;
}

export function WidgetSlider({
  value,
  onChange,
  min,
  max,
  step = 1,
  label,
  showValue = true,
  disabled = false,
  className = '',
}: WidgetSliderProps) {
  return (
    <div className={cn('flex flex-col gap-1', className)}>
      <label className="text-xs text-muted-foreground">
        {label}{showValue && ': '}{showValue && <span className="font-mono">{value}</span>}
      </label>
      <input
        type="range"
        min={min}
        max={max}
        step={step}
        value={value}
        onChange={(e) => onChange(Number(e.target.value))}
        disabled={disabled}
        className="w-full"
      />
    </div>
  );
}

interface WidgetNumberInputProps {
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  label: string;
  disabled?: boolean;
  className?: string;
}

export function WidgetNumberInput({
  value,
  onChange,
  min,
  max,
  step = 1,
  label,
  disabled = false,
  className = '',
}: WidgetNumberInputProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = Number(e.target.value);
    if (min !== undefined && val < min) return;
    if (max !== undefined && val > max) return;
    onChange(val);
  };

  return (
    <div className="flex flex-col gap-1">
      <label className="text-xs text-muted-foreground">{label}</label>
      <input
        type="number"
        value={value}
        onChange={handleChange}
        min={min}
        max={max}
        step={step}
        disabled={disabled}
        className={cn(
          'w-full text-xs border border-border rounded-md px-2 py-1 bg-background',
          className
        )}
      />
    </div>
  );
}

interface WidgetCheckboxProps {
  checked: boolean;
  onChange: (checked: boolean) => void;
  label: string;
  disabled?: boolean;
  className?: string;
}

export function WidgetCheckbox({
  checked,
  onChange,
  label,
  disabled = false,
  className = '',
}: WidgetCheckboxProps) {
  const id = `widget-checkbox-${label.toLowerCase().replace(/\s+/g, '-')}`;
  
  return (
    <div className={cn('flex items-center gap-2', className)}>
      <input
        type="checkbox"
        id={id}
        checked={checked}
        onChange={(e) => onChange(e.target.checked)}
        disabled={disabled}
        className="rounded border-border"
      />
      <label htmlFor={id} className="text-xs text-muted-foreground cursor-pointer">
        {label}
      </label>
    </div>
  );
}
