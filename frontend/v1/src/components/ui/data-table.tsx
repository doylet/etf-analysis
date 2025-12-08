import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react"

const dataTableVariants = cva(
  "w-full border-collapse",
  {
    variants: {
      variant: {
        default: "border border-border rounded-lg overflow-hidden",
        minimal: "border-0",
        striped: "border border-border rounded-lg overflow-hidden [&_tbody_tr:nth-child(even)]:bg-muted/30",
        bordered: "border-2 border-border rounded-lg overflow-hidden",
      },
      size: {
        sm: "[&_th]:px-3 [&_th]:py-2 [&_td]:px-3 [&_td]:py-2 text-sm",
        default: "[&_th]:px-4 [&_th]:py-3 [&_td]:px-4 [&_td]:py-3",
        lg: "[&_th]:px-6 [&_th]:py-4 [&_td]:px-6 [&_td]:py-4 text-base",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface Column<T = Record<string, unknown>> {
  key: string
  header: string
  accessor?: string | ((item: T) => unknown)
  render?: (value: unknown, item: T, index: number) => React.ReactNode
  sortable?: boolean
  align?: "left" | "center" | "right"
  width?: string | number
  className?: string
}

export interface DataTableProps<T = Record<string, unknown>>
  extends React.TableHTMLAttributes<HTMLTableElement>,
    VariantProps<typeof dataTableVariants> {
  data: T[]
  columns: Column<T>[]
  loading?: boolean
  emptyMessage?: string
  sortable?: boolean
  defaultSort?: { key: string; direction: "asc" | "desc" }
  onSort?: (key: string, direction: "asc" | "desc") => void
  striped?: boolean
  hoverable?: boolean
}

type SortState = {
  key: string | null
  direction: "asc" | "desc"
}

const DataTable = React.forwardRef<HTMLTableElement, DataTableProps>(
  ({
    className,
    variant,
    size,
    data,
    columns,
    loading = false,
    emptyMessage = "No data available",
    sortable = true,
    defaultSort,
    onSort,
    striped = false,
    hoverable = true,
    ...props
  }, ref) => {
    const [sortState, setSortState] = React.useState<SortState>({
      key: defaultSort?.key || null,
      direction: defaultSort?.direction || "asc",
    })

    // Internal sorting if no external sort handler provided
    const [sortedData, setSortedData] = React.useState(data)

    React.useEffect(() => {
      if (!onSort && sortState.key) {
        const sorted = [...data].sort((a, b) => {
          const column = columns.find(col => col.key === sortState.key)
          if (!column) return 0

          let aValue: unknown, bValue: unknown

          if (typeof column.accessor === "function") {
            aValue = column.accessor(a)
            bValue = column.accessor(b)
          } else if (typeof column.accessor === "string") {
            aValue = (a as Record<string, unknown>)[column.accessor]
            bValue = (b as Record<string, unknown>)[column.accessor]
          } else {
            aValue = (a as Record<string, unknown>)[column.key]
            bValue = (b as Record<string, unknown>)[column.key]
          }

          // Handle different data types
          if (typeof aValue === "number" && typeof bValue === "number") {
            return sortState.direction === "asc" ? aValue - bValue : bValue - aValue
          }

          if (typeof aValue === "string" && typeof bValue === "string") {
            return sortState.direction === "asc" 
              ? aValue.localeCompare(bValue) 
              : bValue.localeCompare(aValue)
          }

          // Fallback to string comparison
          const aStr = String(aValue || "")
          const bStr = String(bValue || "")
          return sortState.direction === "asc" 
            ? aStr.localeCompare(bStr) 
            : bStr.localeCompare(aStr)
        })
        setSortedData(sorted)
      } else {
        setSortedData(data)
      }
    }, [data, sortState, columns, onSort])

    const handleSort = (columnKey: string) => {
      const column = columns.find(col => col.key === columnKey)
      if (!column?.sortable && !sortable) return

      const newDirection = 
        sortState.key === columnKey && sortState.direction === "asc" 
          ? "desc" 
          : "asc"

      setSortState({ key: columnKey, direction: newDirection })
      
      if (onSort) {
        onSort(columnKey, newDirection)
      }
    }

    const getSortIcon = (columnKey: string) => {
      if (sortState.key !== columnKey) {
        return <ChevronsUpDown className="h-3 w-3 text-muted-foreground" />
      }
      
      return sortState.direction === "asc" 
        ? <ChevronUp className="h-3 w-3 text-foreground" />
        : <ChevronDown className="h-3 w-3 text-foreground" />
    }

    const getAlignmentClass = (align?: string) => {
      switch (align) {
        case "center":
          return "text-center"
        case "right":
          return "text-right tabular-nums"
        default:
          return "text-left"
      }
    }

    const getCellValue = (item: T, column: Column, index: number) => {
      let value: unknown

      if (typeof column.accessor === "function") {
        value = column.accessor(item)
      } else if (typeof column.accessor === "string") {
        value = item[column.accessor]
      } else {
        value = item[column.key]
      }

      if (column.render) {
        return column.render(value, item, index)
      }

      return value
    }

    if (loading) {
      return (
        <div className="w-full">
          <table className={cn(dataTableVariants({ variant, size }), className)} {...props}>
            <thead>
              <tr className="border-b border-border bg-muted/50">
                {columns.map((column) => (
                  <th 
                    key={column.key}
                    className={cn(
                      "font-medium text-foreground border-b border-border",
                      getAlignmentClass(column.align),
                      column.className
                    )}
                    style={{ width: column.width }}
                  >
                    <div className="flex items-center gap-1 opacity-50">
                      {column.header}
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[...Array(3)].map((_, index) => (
                <tr key={index} className="border-b border-border/50">
                  {columns.map((column) => (
                    <td key={column.key} className="border-b border-border/50">
                      <div className="h-4 bg-muted rounded animate-pulse" />
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )
    }

    return (
      <div className="w-full overflow-x-auto">
        <table 
          ref={ref}
          className={cn(
            dataTableVariants({ variant: striped ? "striped" : variant, size }), 
            className
          )} 
          {...props}
        >
          <thead>
            <tr className="border-b border-border bg-muted/50">
              {columns.map((column) => {
                const isSortable = column.sortable !== false && sortable
                
                return (
                  <th 
                    key={column.key}
                    className={cn(
                      "font-medium text-foreground border-b border-border",
                      getAlignmentClass(column.align),
                      isSortable && "cursor-pointer hover:bg-muted/50 transition-colors",
                      column.className
                    )}
                    style={{ width: column.width }}
                    onClick={() => isSortable && handleSort(column.key)}
                  >
                    <div className="flex items-center gap-1">
                      {column.header}
                      {isSortable && getSortIcon(column.key)}
                    </div>
                  </th>
                )
              })}
            </tr>
          </thead>
          <tbody>
            {sortedData.length === 0 ? (
              <tr>
                <td 
                  colSpan={columns.length} 
                  className="text-center text-muted-foreground py-8 border-b border-border/50"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sortedData.map((item, index) => (
                <tr 
                  key={index}
                  className={cn(
                    "border-b border-border/50",
                    hoverable && "hover:bg-muted/30 transition-colors"
                  )}
                >
                  {columns.map((column) => (
                    <td 
                      key={column.key}
                      className={cn(
                        "border-b border-border/50",
                        getAlignmentClass(column.align),
                        column.className
                      )}
                    >
                      {getCellValue(item, column, index)}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    )
  }
)
DataTable.displayName = "DataTable"

export { DataTable, dataTableVariants }