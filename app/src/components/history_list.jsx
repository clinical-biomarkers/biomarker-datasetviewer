import React, { Component } from "react";
import Alertdialog from './dialogbox';
import Loadingicon from "./loading_icon";
import Searchbox from "./search_box";
import * as LocalConfig from "./local_config";
import { Link } from "react-router-dom";
import DoubleArrowOutlinedIcon from '@material-ui/icons/DoubleArrowOutlined';
import { Chart } from "react-google-charts";

import $ from "jquery";


class HistoryList extends Component {
  
  state = {
    ver:"",
    tabidx:"sampleview",
    dialog:{
      status:false, 
      msg:""
    }
  };


  handleKeyPress = (e) => {
    if(e.key === "Enter"){
      e.preventDefault();
      this.handleSearch();
    }
  }


  handleSearch = () => {
    var queryValue = $("#query").val();
    queryValue = (queryValue === undefined ? "" : queryValue);
    var reqObj = {
      "doctype":"track", 
      "dataversion":this.props.initObj.dataversion,
      "query":queryValue
    };
    this.fetchPageData(reqObj);
  }


  handleDialogClose = () => {
    var tmpState = this.state;
    tmpState.dialog.status = false;
    this.setState(tmpState);
  }
  
  handleVersion = () => {
    var ver = $("#verselector").val();
    var reqObj = {"doctype":"track", "dataversion":ver};
    this.fetchPageData(reqObj);
    var tmpState = this.state;
    tmpState.ver = ver;
    this.setState(tmpState);
  }

  fetchPageData(reqObj){
    const requestOptions = { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqObj)
    };
    const svcUrl = LocalConfig.apiHash.dataset_history_list;
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


  componentDidMount() {
    var reqObj = {
      "doctype":"track", 
      "dataversion":this.props.initObj.dataversion,
      "query":""
    };
    this.fetchPageData(reqObj);
  }



  render() {

    if (!("response" in this.state)){
      return <Loadingicon/>
    }
    var pageIdLabel = this.props.pageId.toUpperCase();
    var tableData = this.state.response.tabledata.data;

    var verOptions = [];
    var verList = this.props.initObj.versionlist;
    var selectedVer = (this.state.ver !== "" ? this.state.ver : verList[0]);
    for (var i=0; i < verList.length -1; i++ ){
        var ver = verList[i];
        var lastVer = verList[parseInt(i)+1];
        var lbl = "Changes from v-" + lastVer + " to " + "v-" + ver;
        verOptions.push(<option value={ver}>{lbl}</option>);
    }
    var s = {width:"100%"};
    var verSelector = (
      <select id="verselector" className="form-select" style={s} onChange={this.handleVersion}>{verOptions}
      </select>
    );




    // </div></div>+this.props.pageId} className="reglink">{pageIdLabel}
    return (
      <div className="pagecn">
        <Alertdialog dialog={this.state.dialog} onClose={this.handleDialogClose}/>
        <div className="leftblock" style={{width:"100%", 
          margin:"60px 0px 0px 0px", 
          fontSize:"17px", borderBottom:"1px solid #ccc"}}>
          <DoubleArrowOutlinedIcon style={{color:"#2358C2", fontSize:"17px" }}/>
          &nbsp;
          <Link to="/" className="reglink">HOME </Link> 
            &nbsp; / &nbsp;
          <Link to="/history_list" className="reglink">{pageIdLabel}</Link> 
        </div>


        <div className="leftblock" style={{width:"40%", margin:"40px 0px 0px 0px"}}>
          <div className="leftblock"  style={{width:"90%"}}>
            Select version transition
          </div>
          <span>{verSelector}</span><br/>
        </div>



        <div className="leftblock" style={{width:"100%", margin:"0px 0px 0px 0px"}}>
            <Chart 
                width={'100%'}
                chartType="Table" 
                loader={<div>Loading Chart</div>}
                data={tableData}
                options={
                    {
                        showRowNumber: false, width: '100%', height: '100%',
                        page:'enable', 
                        pageSize:50, 
                        allowHtml:true, 
                        cssClassNames:{
                            headerRow: 'googleheaderrow',
                            tableRow:'googlerow', 
                            oddTableRow:'googleoddrow',
                            headerCell:'googleheadercell',
                            tableCell:'googlecell'
                        }
                    }
                }
                rootProps={{ 'data-testid': '1' }}   
          />
        </div>


      </div>
    );
  }
}

export default HistoryList;

