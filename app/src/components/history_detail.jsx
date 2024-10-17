import React, { Component } from "react";
import Alertdialog from './dialogbox';
import Loadingicon from "./loading_icon";
import * as LocalConfig from "./local_config";
import { Link } from "react-router-dom";
import DoubleArrowOutlinedIcon from '@material-ui/icons/DoubleArrowOutlined';
import { Chart } from "react-google-charts";

import $ from "jquery";


class HistoryDetail extends Component {
  
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

    var reqObj = {"bcoid":this.props.bcoId, dataversion:this.props.dataVersion, doctype:"pairs"};
    const requestOptions = { 
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(reqObj)
    };
    const svcUrl = LocalConfig.apiHash.dataset_history_detail;


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

    var recordObj = this.state.response.record;

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
          <Link to={ "/" + this.props.bcoId + "/" + this.props.dataVersion +"/history"} className="reglink">HISTORY DETAIL</Link> 
        </div>
        <div className="leftblock" style={{width:"100%", margin:"40px 0px 0px 0px"}}>
            <div className="leftblock"  style={{width:"20%", margin:"0px 0px 0px 0px"}}>
                BCO ID<br/>
                <input className="form-control" style={{width:"100%"}} value={recordObj.bcoid}/>
            </div>
            <div className="leftblock" style={{width:"50%",margin:"0px 0px 0px 10px"}}>
                File Name(s)<br/> 
                <input className="form-control" style={{width:"100%"}} value={recordObj.history.file_name}/>
            </div>
            <div className="leftblock" style={{width:"20%",margin:"0px 0px 0px 10px"}}>
                Release Date<br/>
                <input className="form-control" style={{width:"100%"}} value={recordObj.history.release_date}/>
            </div>
            <div className="leftblock" style={{width:"20%",margin:"20px 0px 0px 0px"}}>
                Field Count<br/> 
                <input className="form-control" style={{width:"100%"}} value={recordObj.history.field_count}/>
            </div>
            <div className="leftblock" style={{width:"50%",margin:"20px 0px 0px 10px"}}>
                Row Count<br/>
                <input className="form-control" style={{width:"100%"}} value={recordObj.history.row_count}/>
            </div>
            <div className="leftblock" style={{width:"20%",margin:"20px 0px 0px 10px"}}>
                RecordID Count<br/>
                <input className="form-control" style={{width:"100%"}} value={recordObj.history.id_count}/>
            </div>
            <div className="leftblock" style={{width:"50%",margin:"20px 0px 0px 0px"}}>
                Fields Added ({("fields_added" in recordObj.history ? recordObj.history.fields_added.length : 0)})<br/> 
                <div className="leftblock" style={{width:"100%", height:"100px", overflow:"auto",background:"#fff", padding:   "10px"}}>
                  <pre>{ ("fields_added" in recordObj.history ? recordObj.history.fields_added.join("\n") : "") } </pre>
                </div>
            </div>
            <div className="leftblock" style={{width:"40%",margin:"20px 0px 0px 10px"}}>
                Fields Removed({("fields_removed" in recordObj.history ? recordObj.history.fields_removed.length : 0)})<br/>
                <div className="leftblock" style={{width:"100%", height:"100px", overflow:"auto",background:"#fff", padding:   "10px"}}>
                  <pre>{ ("fields_removed" in recordObj.history ? recordObj.history.fields_removed.join("\n") : "") }</pre>
                </div>
            </div>
            <div className="leftblock" style={{width:"50%",margin:"20px 0px 0px 0px"}}>
                RecordIDs Added({("ids_added" in recordObj.history ? recordObj.history.ids_added.length : 0)})<br/>
                <div className="leftblock" style={{width:"100%", height:"100px", overflow:"auto",background:"#fff", padding:   "10px"}}>
                  <pre>{ ("ids_added" in recordObj.history ? recordObj.history.ids_added.join("\n") : "") }</pre>
                </div>
            </div>
            <div className="leftblock" style={{width:"40%",margin:"20px 0px 0px 10px"}}>
                RecordIDs Removed({("ids_removed" in recordObj.history ? recordObj.history.ids_removed.length : 0)})<br/>
                <div className="leftblock" style={{width:"100%", height:"100px", overflow:"auto",background:"#fff", padding:"10px"}}>
                  <pre>{ ("ids_removed" in recordObj.history ? recordObj.history.ids_removed.join("\n") : "") }</pre>
                </div>
            </div>
          </div>
      </div>
    );
  }
}

export default HistoryDetail;

