import React, { Component } from "react";
import DatasetSearch from "./components/dataset_search";
import DatasetList from "./components/dataset_list";
import RecordList from "./components/record_list";
import StaticPage from "./components/static_page";
import HistoryList from "./components/history_list";
import HistoryDetail from "./components/history_detail";
import FileUploads from "./components/file_uploads";
import GlycanFinder from "./components/glycan_finder";

import Alertdialog from './components/dialogbox';
import Loadingicon from "./components/loading_icon";
import * as LocalConfig from "./components/local_config";
import "./App.css";
import { BrowserRouter as Router, Switch, Route } from "react-router-dom";
import Header from "./components/header";
import Footer from "./components/footer";
import Gsd from "./components/gsd";




class App extends Component {

  state = {
    dialog:{
      status:false, 
      msg:""
    }
  };



  handleDialogClose = () => {
    var tmpState = this.state;
    tmpState.dialog.status = false;
    this.setState(tmpState);
  }

  componentDidMount() {
    var reqObj = {};
    const requestOptions = {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqObj)
    };
    const svcUrl = LocalConfig.apiHash.dataset_init;

    fetch(svcUrl, requestOptions)
      .then((res) => res.json())
      .then(
        (result) => {
          var tmpState = this.state;
          tmpState.response = result;
          tmpState.isLoaded = true;
          if (tmpState.response.status === 0){
            tmpState.dialog.status = true;
            tmpState.dialog.msg = tmpState.response.error;
          }
          this.setState(tmpState);
          //console.log("Request:",svcUrl);
          console.log("Ajax response:", result);
        },
        (error) => {
          this.setState({
            isLoaded: true,
            error,
          });
        }
      );
  }


  render() {
    
    if (!("response" in this.state)){
      return <Loadingicon/>
    }


    var app_ver = process.env.REACT_APP_APP_VERSION;
    var data_ver = this.state.response.record.dataversion;

    return (
      <div>
      <Alertdialog dialog={this.state.dialog} onClose={this.handleDialogClose}/>
      <Header onSearch={this.handleSearch} onKeyPress={this.handleKeyPress} initObj={this.state.response.record}/>
      <div className="versioncn">APP v-{app_ver} &nbsp; |&nbsp; Data v-{data_ver}</div>
      <Router>
        <Switch>
        <Route
            path="/gsd"
            render={(props) => (
              <Gsd initObj={this.state.response.record}/>
            )}
          />
          <Route
            path="/glycan_finder"
            render={(props) => (
              <GlycanFinder pageId={"glycanfinder"} initObj={this.state.response.record}/>
            )}
          />
          <Route
            path="/uploads"
            render={(props) => (
              <FileUploads pageId={"File Uploads"} initObj={this.state.response.record}/>
            )}
          />
          <Route
            path="/history_list"
            render={(props) => (
              <HistoryList pageId={"History List"}  initObj={this.state.response.record}/>
            )}
          />
        <Route
            exact
            path="/results/:listId"
            render={(props) => (
            <DatasetList  initObj={this.state.response.record} listId={props.match.params.listId}/>
            )}
          />
        <Route
            path="/:bcoId/:dataVersion/history"
            render={(props) => (
              <HistoryDetail bcoId={props.match.params.bcoId} dataVersion={props.match.params.dataVersion}  initObj={this.state.response.record}/>
            )}
          />
          <Route
            path="/static/:pageId"
            render={(props) => (
              <StaticPage pageId={props.match.params.pageId}  initObj={this.state.response.record}/>
            )}
        />
        <Route
            path="/:bcoId"
            render={(props) => (
              <RecordList bcoId={props.match.params.bcoId} initObj={this.state.response.record}/>
            )}
        />
        <Route
            exact
            path="/"
            render={(props) => (
              <DatasetSearch  initObj={this.state.response.record}/>
            )}
          />
        </Switch>
      </Router>
      <Footer initObj={this.state.response.record}/>
      </div>
    );

    
  }
}

export default App;
