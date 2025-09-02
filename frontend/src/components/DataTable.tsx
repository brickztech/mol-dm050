import * as React from "react";
import { DataGrid, type GridColDef } from "@mui/x-data-grid";
import { ThemeProvider, createTheme } from "@mui/material/styles";
import type { PaletteMode } from "@mui/material";

export type Row = { id?: string | number } & Record<string, any>;

export default function DataTable({
                                      columns,
                                      rows,
                                      mode = "light",
                                  }: {
    columns: GridColDef[];
    rows: Row[];
    mode?: PaletteMode;
}) {
    const theme = React.useMemo(() => createTheme({ palette: { mode } }), [mode]);

    return (
        <div style={{ display: "flex", flexDirection:"column", width: "100%" }}>
            <ThemeProvider theme={theme}>
                <DataGrid
                    rows={rows}
                    columns={columns}
                    pageSizeOptions={[5, 10, 20]}
                    pagination
                    autoHeight={true}
                    initialState={{
                        pagination: { paginationModel: { pageSize: 5, page: 0 } },
                    }}
                    density="compact"
                    sx={{
                        bgcolor: "background.paper",
                        "& .MuiDataGrid-cell": {
                            borderBottom: "1px solid",
                            borderColor: "divider",
                        },
                    }}
                />
            </ThemeProvider>
        </div>

    );
}
