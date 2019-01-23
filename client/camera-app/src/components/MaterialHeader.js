import React, { Component } from 'react'
import PropTypes from 'prop-types';
import { withStyles } from '@material-ui/core/styles';

/* Material UI */
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';

/* Styles util */
import * as styles from '../utils/styles';

/* React Router */
import { Link } from 'react-router-dom';

class MaterialHeader extends Component {
  state = {
    headerTitle: 'Camera tracking with OpenCV'
  };
  render() {
    const { classes } = this.props;
    const { headerTitle } = this.state;
    return (
      <div >
        <AppBar position="static" className={classes.root}>
          <Toolbar>

            <Typography variant="h6" color="inherit" className={classes.grow}>
              <Link style={{ textDecoration: 'none', color: '#ffffff' }} to="/">
                {headerTitle}
              </Link>
            </Typography>

            <Button color="inherit">
              <Link style={{ textDecoration: 'none', color: '#ffffff' }} to="/about">
                About
              </Link>
            </Button>

          </Toolbar>
        </AppBar>
      </div>
    )
  }
}

MaterialHeader.propTypes = {
  classes: PropTypes.object.isRequired,
};

/* We can use this way theme with material ui */
export default withStyles(styles.default.headerStyles)(MaterialHeader);