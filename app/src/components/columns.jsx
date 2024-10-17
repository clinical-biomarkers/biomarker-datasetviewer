import * as React from 'react';
import { Link } from "react-router-dom";


export function getColumns(key){

  var colDict = {
    toy:[
      {
        field: 'id',
        headerName: 'ID',
        width: 120,
        headerClassName:"dgheader",
        cellClassName:"dgcell"
      },
      {
        field: 'fname',
        headerName: 'FIRST NAME',
        width: 300,
        headerClassName:"dgheader",
        cellClassName:"dgcell"
      }
    ],
    tableone:[
      {
        field: 'id', 
        headerName: 'BCO ID', 
        width: 130, 
        headerClassName:"dgheader", 
        cellClassName:"dgcell"
      },
      {
        field: 'description',
        headerName: 'DESCRIPTION',
        width: 300,
        headerClassName:"dgheader",
        cellClassName:"dgcell"
      },
      {
        field: 'filename',
        headerName: 'FILE NAME',
        width: 300, 
        headerClassName:"dgheader", 
        cellClassName:"dgcell" 
      },
      {
        field: 'title',
        headerName: 'BCO TITLE',
        width: 250, 
        headerClassName:"dgheader", 
        cellClassName:"dgcell" 
      },
      {
        field: 'details',
        headerName: 'DETAILS',
        width: 150, 
        headerClassName:"dgheader", 
        cellClassName:"dgcell",
        renderCell: (params) => (
          <span>
            <span>{params.value.rowlist.length > 0 ? params.value.rowlist.length + " row(s) found" : "" }</span>
            <Link
              className="reglink"
              to={
                {
                  pathname: "/" + params.value.bcoid,
                  state: {rowlist: params.value.rowlist}
                }
              }
              >
                {params.value.label}
              </Link>
            </span>
        ),
        sortComparator: (v1, v2) => v1.name.localeCompare(v2.name)
      }
    ],
    tabletwo:[

    ]
  };

  return colDict[key]
}



