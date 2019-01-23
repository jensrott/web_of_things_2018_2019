import React, { Component } from 'react';
import PropTypes from 'prop-types';

/* Material UI */
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import TableCell from '@material-ui/core/TableCell';
import Checkbox from '@material-ui/core/Checkbox';
import Tooltip from '@material-ui/core/Tooltip';
import TableSortLabel from '@material-ui/core/TableSortLabel';

/* Rows for header to loop over */
const rows = [
  { id: 'date', numeric: true, label: 'Date' },
  { id: 'count_items', numeric: true, label: 'Tracked Items' },
];

class TableHeader extends Component {
  createSortHandler = property => event => {
    this.props.onRequestSort(event, property);
  };
  render() {

    const { onSelectAllClick, order, orderBy, numSelected, rowCount } = this.props;

    return (
      <TableHead>
        <TableRow>
          <TableCell padding="checkbox">
            <Checkbox
              indeterminate={numSelected > 0 && numSelected < rowCount}  // - sign if not all items (rows) are selected
              checked={numSelected === rowCount} // Checked if all items are selected 
              onChange={onSelectAllClick} // When we select all checkboxes
            />
          </TableCell>
          {rows.map(
            row => (
              <TableCell
                key={row.id}
                align={'center'}
                padding={'dense'}
                sortDirection={orderBy === row.id ? order : false}
              >
                <Tooltip
                  title="Sort"
                  placement={row.numeric ? 'bottom-end' : 'bottom-start'}
                  enterDelay={300}
                >
                  <TableSortLabel
                    active={orderBy === row.id}
                    direction={order}
                    onClick={this.createSortHandler(row.id)}
                  >
                    {row.label}
                  </TableSortLabel>
                </Tooltip>
              </TableCell>
            ),
            this,
          )}
        </TableRow>
      </TableHead>
    )
  }
}

TableHeader.propTypes = {
  onRequestSort: PropTypes.func.isRequired,
  onSelectAllClick: PropTypes.func.isRequired,
  order: PropTypes.string.isRequired,
  orderBy: PropTypes.string.isRequired,
  numSelected: PropTypes.number.isRequired,
  rowCount: PropTypes.number.isRequired,
};

export default TableHeader
