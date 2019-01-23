import React, { Component } from 'react';
import PropTypes from 'prop-types';

/* Own components */
import TableHeader from './TableHeader';
import TableToolBar from './TableToolBar';

/* Styles util */
import * as styles from '../utils/styles';

/* Material UI */
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableRow from '@material-ui/core/TableRow';
import Paper from '@material-ui/core/Paper';
import Checkbox from '@material-ui/core/Checkbox';
import { withStyles } from '@material-ui/core/styles';

/* Moment.js */
import moment from 'moment/moment.js';

/* Firebase, Firestore */
import firebase from '@firebase/app';
import firebaseConfig from '../keys/firebaseConfig';
import '@firebase/firestore';

firebase.initializeApp(firebaseConfig);

const firestore = firebase.firestore();
firestore.settings({ timestampsInSnapshots: true });

class FacesTrackedResults extends Component {

  state = {
    order: 'asc',
    orderBy: 'date',
    selected: [], // array, containing the selected rows
    arrayObject: [], // array, containing the objects retrieved from Firestore

    /* For reloading the page */
    loading: false,
    succes: false
  };

  componentDidMount() {
    const { orderBy, order } = this.state;
    this.getThemAll(orderBy, order);
  }

  /**
   * Fetches all the data from firestore and put the data and additional data in a new object and push it in an array.
   * That way we can map over it and show the data.
   */
  getThemAll = (orderBy, order) => { // Function to get all items from the database instead of one item
    firestore.collection('faces_tracked').orderBy(orderBy, order).get().then((snapshot) => {
      let newArray = []; // Array we use to put data to the state
      snapshot.docs.forEach(doc => {

        /* Manipulation of date from firestore with moment.js */
        let timeStamp = doc.data().date.toDate(); // We get the timestamp from firestore
        let localConverted = moment(timeStamp).local().format('DD-MM-YYYY HH:mm:ss'); // We convert the timestamp with moment.js to a better format

        /* Create a new object so we can store all of it in an array */
        let newObject = {};
        // newObject.date = cleanDate;
        newObject.documentId = doc.id; // The document ids
        newObject.dayDate = localConverted // The date in a clean format
        newObject.firebase = doc.data(); // All the firebase data
        newArray.push(newObject); // Push the object clean in an array
      });

      this.setState({ arrayObject: newArray }) // Set the state to an array so we can map over it
      /* Uncomment these two lines to see all the data in firestore */
      // console.log(this.state.arrayObject);
      // console.log(this.state.arrayObject[0].documentId);
    }).catch(err => console.log(err));
  }

  /** 
   * Selects all the checkbox and handles the other checkboxes accordingly
   * @param {any} event
   * @return {Array} All the indexes of the array
   */
  handleSelectAllClick = event => {
    if (event.target.checked) {
      let mappedArrayIndex = this.state.arrayObject.map((data, index) => index)
      this.setState(({ selected: mappedArrayIndex })); // Map over the data in the arrayObject array, We get the index so it knows to select all of them
      return;
    } // Else empty array
    this.setState({ selected: [] });
  };

  /** 
   * Handles every checkbox
   * @param {any} event
   * @param {string} id
   */
  handleClick = (event, id) => {
    const { selected } = this.state;
    const selectedIndex = selected.indexOf(id);
    let newSelected = [];

    /* Handles which of the checkboxes are selected */
    if (selectedIndex === -1) {
      newSelected = newSelected.concat(selected, id); // join two or more arrays
    } else if (selectedIndex === 0) {
      newSelected = newSelected.concat(selected.slice(1));
    } else if (selectedIndex === selected.length - 1) {
      newSelected = newSelected.concat(selected.slice(0, -1));
    } else if (selectedIndex > 0) {
      newSelected = newSelected.concat(
        selected.slice(0, selectedIndex),
        selected.slice(selectedIndex + 1),
      );
    }
    console.log(newSelected);
    this.setState({ selected: newSelected });
  };

  /** 
   * Deletes the item from firestore and reload the table realtime
   */
  handleDeleteItem = () => { // Arrow functions are not needed here i don't know why but I keep it here to keep it clean
    const { selected, arrayObject, orderBy, order } = this.state; // array containing the indices of the items which are selected to be deleted
    console.log(selected); // With selected we can delete

    for (let i = 0; i < selected.length; i++) {
      let documentId = arrayObject[selected[i]].documentId;
      console.log(documentId);
      firestore.collection('faces_tracked').doc(documentId).delete().then(() => {
        console.log(`Succesfully deleted ${documentId}`);
      }).catch(err => console.log(err));
    }
    /* To reload the page real time */
    this.setState({ selected: [] });
    this.getThemAll(orderBy, order);
  }

  /** 
    * Refreshes the table by fetching all the items in the database.
    * Also do a fancy spin animation
    */
  handleRefreshTable = () => {
    const { orderBy, order } = this.state;
    // Loading animation happens in TableToolBar.js
    this.getThemAll(orderBy, order);
    this.setState({ selected: [] });
  }

  /** 
   * Function to determine to switch between asc or desc sorting
   * @param {any} property
   */
  handleRequestSort = (event, property) => {
    const orderBy = property;
    let order = 'desc';

    if (this.state.orderBy === property && this.state.order === 'desc') {
      order = 'asc';
    }

    // console.log(order); // desc, asc, desc, asc...
    // console.log(orderBy); // date, count_items
    this.getThemAll(orderBy, order);
    this.setState({ selected: [], order, orderBy });
  };

  /** 
   * Function to determine if the row is selected or not. 
   * Selected is true. Not selected is false.
   * @param {number} id
   */
  isSelected = id => this.state.selected.indexOf(id) !== -1; // returns true if item with index "id" is selected

  render() {
    /* Destructering to get the data easier */
    const { classes } = this.props;
    const { order, orderBy, selected, arrayObject } = this.state;
    return (
      <Paper className={classes.root}>

        {/* Seperate component TableToolBar */}
        <TableToolBar
          numSelected={selected.length}
          name='Faces Tracked'
          onDeleteItem={this.handleDeleteItem.bind(this)}
          onRefreshTable={this.handleRefreshTable.bind(this)} />

        <div className={classes.tableWrapper}>
          <Table className={classes.table} aria-labelledby="tableTitle">

            {/* Seperate component TableHeader */}
            <TableHeader
              numSelected={selected.length}  // number of items selected
              order={order}
              orderBy={orderBy}
              onSelectAllClick={this.handleSelectAllClick}
              onRequestSort={this.handleRequestSort} //To sort
              rowCount={arrayObject.length} />

            <TableBody>

              {/* We loop over the items in firestore */}
              {arrayObject.map((data, index) => {
                // console.log(index);
                const isSelected = this.isSelected(index);
                return (
                  <TableRow
                    hover
                    onClick={event => this.handleClick(event, index)}
                    role="checkbox"
                    aria-checked={isSelected}
                    tabIndex={-1}
                    key={index}
                    selected={isSelected}
                  >

                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={isSelected}
                      />
                    </TableCell>
                    <TableCell align={'center'}>{data.dayDate}</TableCell>
                    <TableCell align={'center'}>{data.firebase.count_items}</TableCell>

                  </TableRow>
                )
              })}
            </TableBody>

          </Table>
        </div>
      </Paper>
    )
  }
}

FacesTrackedResults.propTypes = {
  classes: PropTypes.object.isRequired,
};

/* We can use this way theme with material ui */
export default withStyles(styles.default.mainStyles)(FacesTrackedResults);
