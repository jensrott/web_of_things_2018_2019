import React, { Component } from 'react'
import PropTypes from 'prop-types';

/* Material UI */
import Typography from '@material-ui/core/Typography';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import { withStyles } from '@material-ui/core/styles';

/* Styles util */
import * as styles from '../utils/styles';

class About extends Component {
  render() {
    const { classes } = this.props;
    return (
      <React.Fragment>
        <div className={classes.root}>
          <Typography variant="h3" gutterBottom>
            About
          </Typography>
        </div>
        <div>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6" >What is it?</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                I made an app that communicates with a Raspberry Pi Camera that tracks the amount of faces and eyes per day.
                OpenCv and Dlib are being used to detect and track faces and eyes.
                The data is being stored and fetched from Firestore.
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>

          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6" >Technologies used</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                <li>
                  React
                </li>
                <li>
                  React-Router
                </li>
                <li>
                  Material-UI
                </li>
                <li>
                  Firestore
                </li>
                <li>
                  Raspberry Pi
                </li>
                <li>
                  Python
                </li>
                <li>
                  OpenCV
                </li>
                <li>
                  Dlib
                </li>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6" >Made by</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                <a style={{ textDecoration: 'none', color: '#3f51b5' }} href="https://github.com/jensrott"> Jens Rottiers</a>
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
          <ExpansionPanel>
            <ExpansionPanelSummary expandIcon={<ExpandMoreIcon />}>
              <Typography variant="h6" >Version</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <Typography>
                1.0
              </Typography>
            </ExpansionPanelDetails>
          </ExpansionPanel>
        </div>
      </React.Fragment>
    )
  }
}

About.propTypes = {
  classes: PropTypes.object.isRequired,
};

/* We can use this way theme with material ui */
export default withStyles(styles.default.AboutStyles)(About);