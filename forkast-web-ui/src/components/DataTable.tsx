import React from 'react';

export interface Column<T> {
  header: string;
  accessor: keyof T | ((item: T) => React.ReactNode);
  className?: string;
}

interface DataTableProps<T> {
  data: T[];
  columns: Column<T>[];
  keyField: keyof T;
}

export const DataTable = <T,>({ data, columns, keyField }: DataTableProps<T>) => {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-700 bg-slate-800/50">
      <table className="w-full text-left border-collapse">
        <thead className="bg-slate-900/50 text-slate-400 text-xs uppercase tracking-wider">
          <tr>
            {columns.map((col, idx) => (
              <th key={idx} className={`p-4 font-semibold ${col.className || ''}`}>
                {col.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className="divide-y divide-slate-700/50 text-slate-200 text-sm">
          {data.map((item) => (
            <tr key={String(item[keyField])} className="hover:bg-white/5 transition">
              {columns.map((col, idx) => (
                <td key={idx} className={`p-4 ${col.className || ''}`}>
                  {typeof col.accessor === 'function' 
                    ? col.accessor(item) 
                    : (item[col.accessor] as React.ReactNode)}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};
