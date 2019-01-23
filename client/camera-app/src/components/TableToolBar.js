import React, { Component } from 'react'
import PropTypes from 'prop-types';
import classNames from 'classnames';

/* Material UI */
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';
import IconButton from '@material-ui/core/IconButton';
import DeleteIcon from '@material-ui/icons/Delete';
import CircularProgress from '@material-ui/core/CircularProgress';
import RotateRight from '@material-ui/icons/RotateRight';
import Fab from '@material-ui/core/Fab';
import CheckIcon from '@material-ui/icons/Check';
import { withStyles } from '@material-ui/core/styles';

/* Styles util */
import * as styles from '../utils/styles';

class TableToolBar extends Component {
  state = {
    loading: false,
    succes: false
  }
  componentWillUnmount() {
    clearInterval(this.timer);
  }

  handleReload = event => {
    // Animation
    if (!this.state.loading) {
      this.setState(
        {
          success: false,
          loading: true,
        },
        () => {
          this.timer = setTimeout(() => {
            this.setState({
              loading: false,
              success: true,
            });
          }, 800);
        },
        // TODO fix that after green icon turns back to red
        this.setState({ loading: false, success: false })
      );
    }
    // Fetching of the data happens in FacesTrackedResults
    this.props.onRefreshTable(event);
  };

  DeleteItem = event => id => {
    this.props.onDeleteItem(event, id)
  };
  render() {

    const { numSelected, classes, name } = this.props;
    const { loading, success } = this.state;
    const buttonClassname = classNames({
      [classes.buttonSuccess]: success,
    });

    return (
      <Toolbar
        className={classNames(classes.root, {
          [classes.highlight]: numSelected > 0,
        })}
      >
        <div className={classes.title}>
          {numSelected > 0 ? (
            <Typography color="inherit" variant="subtitle1">
              {numSelected} selected
          </Typography>
          ) : (
              <Typography variant="h6" id="tableTitle">
                {name}
              </Typography>
            )}
        </div>
        <div className={classes.actions}>
          {numSelected > 0 ? ( // If items are selected show the DeleteIcon
            <Tooltip title="Delete">
              <IconButton aria-label="Delete" onClick={this.DeleteItem()}>
                <DeleteIcon />
              </IconButton>
            </Tooltip>
          ) : ( // Else show the reload table button
              <Tooltip title="Refresh Table">
                <div className={classes.rootProgress}>
                  <div className={classes.wrapper}>
                    <Fab color="secondary" className={buttonClassname} onClick={this.handleReload.bind(this)}>
                      {success ? <CheckIcon /> : <RotateRight />}
                    </Fab>
                    {loading && <CircularProgress size={68} className={classes.fabProgress} />}
                  </div>
                </div>
              </Tooltip>
            )}
        </div>
      </Toolbar>
    )
  }
}

/* Shows us what type of data a component requires to render properly */
TableToolBar.propTypes = {
  onRefreshTable: PropTypes.func.isRequired,
  onDeleteItem: PropTypes.func.isRequired,
  numSelected: PropTypes.number.isRequired,
  classes: PropTypes.object.isRequired,
  name: PropTypes.string.isRequired,
};


/* We can use this way theme with material ui */
export default withStyles(styles.default.toolbarStyles)(TableToolBar);
