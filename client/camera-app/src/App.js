import React from 'react';

/* React Router */
import { BrowserRouter as Router, Route } from 'react-router-dom';

/* Own components */
import MaterialHeader from './components/MaterialHeader';

/* EyesTrackedResults and FacesTrackedResults combined here */
import About from './components/About';
import Home from './components/Home';

const App = () =>

  <Router>
    <React.Fragment>
      <MaterialHeader />
      <Route exact path="/about" component={About} />
      <Route exact path="/" component={Home} />
    </React.Fragment >
  </Router>

export default App;
