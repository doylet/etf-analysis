import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const cardVariants = cva(
  "rounded-lg border bg-card text-card-foreground transition-all duration-200",
  {
    variants: {
      variant: {
        default: "shadow-sm hover:shadow-md",
        professional: "shadow-md border-border bg-card hover:shadow-lg",
        elevated: "shadow-lg border-border bg-card",
        subtle: "shadow-sm border-border bg-muted/50 hover:bg-card hover:shadow-md",
        data: "shadow-sm border-border bg-card hover:shadow-md tabular-nums",
        outlined: "shadow-none border-2 border-border hover:border-muted-foreground",
      },
      size: {
        sm: "p-4",
        default: "",
        lg: "p-8",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, size, className }))}
      {...props}
    />
  )
)
Card.displayName = "Card"

const cardHeaderVariants = cva(
  "flex flex-col space-y-1.5",
  {
    variants: {
      size: {
        sm: "p-4 space-y-1",
        default: "p-6 space-y-1.5", 
        lg: "p-8 space-y-2",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof cardHeaderVariants>
>(({ className, size, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(cardHeaderVariants({ size, className }))}
    {...props}
  />
))
CardHeader.displayName = "CardHeader"

const CardAction = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center", className)}
    {...props}
  />
))
CardAction.displayName = "CardAction"

const cardTitleVariants = cva(
  "font-semibold leading-none tracking-tight",
  {
    variants: {
      size: {
        sm: "text-lg",
        default: "text-2xl",
        lg: "text-3xl",
      },
      variant: {
        default: "",
        professional: "text-foreground font-medium",
        data: "tabular-nums",
      },
    },
    defaultVariants: {
      size: "default",
      variant: "default",
    },
  }
)

const CardTitle = React.forwardRef<
  HTMLHeadingElement,
  React.HTMLAttributes<HTMLHeadingElement> & VariantProps<typeof cardTitleVariants>
>(({ className, size, variant, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(cardTitleVariants({ size, variant, className }))}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const cardContentVariants = cva(
  "",
  {
    variants: {
      size: {
        sm: "p-4 pt-0",
        default: "p-6 pt-0",
        lg: "p-8 pt-0",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof cardContentVariants>
>(({ className, size, ...props }, ref) => (
  <div 
    ref={ref} 
    className={cn(cardContentVariants({ size, className }))} 
    {...props} 
  />
))
CardContent.displayName = "CardContent"

const cardFooterVariants = cva(
  "flex items-center",
  {
    variants: {
      size: {
        sm: "p-4 pt-0",
        default: "p-6 pt-0",
        lg: "p-8 pt-0",
      },
    },
    defaultVariants: {
      size: "default",
    },
  }
)

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement> & VariantProps<typeof cardFooterVariants>
>(({ className, size, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(cardFooterVariants({ size, className }))}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardAction, CardFooter, CardTitle, CardDescription, CardContent }
