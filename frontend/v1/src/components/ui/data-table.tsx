import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { ChevronUp, ChevronDown, ChevronsUpDown } from "lucide-react"

const dataTableVariants = cva(
  "w-full border-collapse",
  {
    variants: {
      variant: {
        default: "border border-gray-200 rounded-lg overflow-hidden",
        minimal: "border-0",
        striped: "border border-gray-200 rounded-lg overflow-hidden [&_tbody_tr:nth-child(even)]:bg-gray-50/50",
        bordered: "border-2 border-gray-300 rounded-lg overflow-hidden",
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

export interface Column<T = any> {
  key: string
  header: string
  accessor?: string | ((item: T) => any)
  render?: (value: any, item: T, index: number) => React.ReactNode
  sortable?: boolean
  align?: "left" | "center" | "right"
  width?: string | number
  className?: string
}

export interface DataTableProps<T = any>
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

          let aValue: any, bValue: any

          if (typeof column.accessor === "function") {
            aValue = column.accessor(a)
            bValue = column.accessor(b)
          } else if (typeof column.accessor === "string") {
            aValue = (a as any)[column.accessor]
            bValue = (b as any)[column.accessor]
          } else {
            aValue = (a as any)[column.key]
            bValue = (b as any)[column.key]
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
        return <ChevronsUpDown className="h-3 w-3 text-gray-400" />
      }
      
      return sortState.direction === "asc" 
        ? <ChevronUp className="h-3 w-3 text-gray-600" />
        : <ChevronDown className="h-3 w-3 text-gray-600" />
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

    const getCellValue = (item: any, column: Column, index: number) => {
      let value: any

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
              <tr className="border-b border-gray-200 bg-gray-50">
                {columns.map((column) => (
                  <th 
                    key={column.key}
                    className={cn(
                      "font-medium text-gray-900 border-b border-gray-200",
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
                <tr key={index} className="border-b border-gray-100">
                  {columns.map((column) => (
                    <td key={column.key} className="border-b border-gray-100">
                      <div className="h-4 bg-gray-200 rounded animate-pulse" />
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
            <tr className="border-b border-gray-200 bg-gray-50">
              {columns.map((column) => {
                const isSortable = column.sortable !== false && sortable
                
                return (
                  <th 
                    key={column.key}
                    className={cn(
                      "font-medium text-gray-900 border-b border-gray-200",
                      getAlignmentClass(column.align),
                      isSortable && "cursor-pointer hover:bg-gray-100 transition-colors",
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
                  className="text-center text-gray-500 py-8 border-b border-gray-100"
                >
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              sortedData.map((item, index) => (
                <tr 
                  key={index}
                  className={cn(
                    "border-b border-gray-100",
                    hoverable && "hover:bg-gray-50 transition-colors"
                  )}
                >
                  {columns.map((column) => (
                    <td 
                      key={column.key}
                      className={cn(
                        "border-b border-gray-100",
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